#include "GeneticAlgorithm_OA.h"

using namespace NS_NBGA;
using namespace std;

#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <ctime>
#include <iostream>
#include <map>
#include <random>
#include <chrono>

#define VERBOSE_DEBUG 1

GeneticAlgorithm_OA :: GeneticAlgorithm_OA (int pop_size, vector<vector<float>>& ch_struct, Mode mode, bool all_clusters_active, bool short_run)
{
	// check that the population size is even
	if (pop_size != 1 and pop_size % 2 != 0)
	{
		cout << "Population size is " << pop_size << endl;
		throw invalid_argument("Population_size must be even");
	}

 	// current date/time based on current system
 	time_t now = time(0);

	if(short_run == false)
	{
		LogFile = ofstream(LOG_FILE_NAME, ios::out | ios::app);

		if (!LogFile.is_open())
			throw ifstream::failure("Failed to open the log file" + string(LOG_FILE_NAME));

		LogFile << endl << endl << "***************************" << endl;
		LogFile << ctime(&now) << "***************************" << endl;

		// open the file to write down the coordinates of feasible members of the Pareto optimal fronts
        //if(VERBOSE_DEBUG)
        //    ObjFile = ofstream(FRONT_EVO_FILE, ios::out | ios::app);
	}


	population_size = pop_size;
	gene_length = ch_struct.size();


	// at least one of the genes in the gene cluster has to be active if true
	bool always_active = all_clusters_active;

	// form the chromosome from the weights
	for (int i = 0; i < ch_struct.size(); i ++)
		chromosome_struct.push_back(GeneCluster_OA(ch_struct[i].size(), always_active));

	current_mode = mode;

	fast_run = short_run;

	generation_num = 1;

	switch_state(active_state);

	feasible_found = false;

	gen_before_hetacomb = 0;

	// margin of the hetacomb gets increased by 0.05 every 2 hetacombs
	max_hetacomb_counter = (RATIO_BEST_FIT_MARGIN_MAX - RATIO_BEST_FIT_MARGIN_MIN) / 0.05 * 2;


	// initial best fitness value is the maximum
	best_cost = INIT_FIT_VALUE;

	// generation at which the best fitness value was reached
	gen_best_cost = 1;

	best_cost_margin = RATIO_BEST_FIT_MARGIN_MIN * best_cost;

	current_best_cost = INIT_FIT_VALUE;

	// same if there no feasible solutions
	best_feasibility_val = 0;
	gen_best_feasibility_val = 1;
	best_feasibility_margin = 0;

	current_best_feasibility = 0;

	// initialize the mutation pattern
	row_of_mutation_matrix = round(gene_length * RATIO_OF_GENES_MUTATED_INIT);

	if (row_of_mutation_matrix < 3)
		row_of_mutation_matrix = 3;

	if (short_run == false && VERBOSE_DEBUG)
		LogFile << endl << row_of_mutation_matrix << " genes are flipped out of " << gene_length << endl;


	vector<int> temp;
	int counter = 0;

	// fill row_of_mutation_matrix vectors with numbers from 0 to row_of_mutation_matrix * row_of_mutation_matrix
	for (int i = 0; i < row_of_mutation_matrix; i ++)
	{
		temp.clear();

		for (int j = 0; j < row_of_mutation_matrix; j ++)
			temp.push_back(counter++);

		mutation_prob_vect.push_back(temp);
	}


	// row indexes are counted from 0
	row_of_mutation_matrix --;

	if (short_run == false && VERBOSE_DEBUG)
	{
		for(int i = 0; i < mutation_prob_vect.size(); i ++)
		{
			for (int j = 0; j < mutation_prob_vect[i].size(); j ++)
				LogFile << mutation_prob_vect[i][j] << " ";

			LogFile << endl;
		}
		LogFile << endl;
	}
}


GeneticAlgorithm_OA :: ~GeneticAlgorithm_OA()
{
	if(fast_run == false)
	{
		time_t now = time(0);

		LogFile << endl << endl << "**********THE END***********" << endl;
		LogFile << ctime(&now) << "***************************" << endl;

		LogFile.close();
        
        if(VERBOSE_DEBUG)
            ObjFile.close();
	}
}


int GeneticAlgorithm_OA :: first_generation()
{   
    // pass this to the GA_Solution to compare different tree establishments properly
    bool permutable = false;

    if(current_mode == Tree_Establishment_single || current_mode == Tree_Establishment_multi)
        permutable = true;

	// set the default ordering: 0, 1, 2, ... for every solution
	vector<int> ordering_default;
	for(int i = 0; i < chromosome_struct.size(); i ++)
		ordering_default.push_back(i);

	for (int i = 0; i < population_size; i ++)
	{
		if(current_mode == Ordering)
		{
			random_shuffle(ordering_default.begin(), ordering_default.end());
			population.push_back(GA_Solution_OA(chromosome_struct, ordering_default, permutable));
		}

		// randomly generate the first generation
		else
			population.push_back(GA_Solution_OA(chromosome_struct, permutable));

        if(current_mode == OA_placement_multi || current_mode == Tree_Establishment_multi || current_mode == RSA_multi)
        {
            // set the rank to zero
            front_number.push_back(0);

            // set the crowding distance to zero
            crowding_distances.push_back(0);
        }
	}

	new_population = population;

	if(current_mode == OA_placement_single || current_mode == OA_placement_multi)
	{
		// read the file with the initial placements
		ifstream InitFile(INIT_FILE_NAME_OA, ios::in);

		if (!InitFile.is_open())
			throw ifstream::failure("Failed to open the init file" + string(INIT_FILE_NAME_OA));

		int amp_counter;
		int start, end;
		string buf, data;
		string s_init_placement = "Initial placement";

		int init_placement_num, cand_location_id;

		vector<bool>temp;


		while(!InitFile.eof())
		{
			// first line
			getline(InitFile, buf);

			// if it's commented, skip
			if (buf.find("//") != -1)
				continue;

			// skip the title
			start = buf.find(s_init_placement);
			if (start == string::npos)
				continue;

			// read the number and get rid of the spaces
			data = buf.substr(start + s_init_placement.length());
			data.erase( remove_if( data.begin(), data.end(), ::isspace ), data.end() );

			// the number of the members in the population
			init_placement_num = stoi(data);

			// no overflow
			if (init_placement_num >= population_size)
				throw invalid_argument("Initial placement is out of range");
			
			amp_counter = 0;

			// second line
			getline(InitFile, buf);

			// extract the id list from the brackets
			start = buf.find("<");
			end = buf.find(">");

			if (start == string::npos || end == string::npos)
				continue;

			buf = buf.substr(start + 1, end - start - 1);

			// delete the spaces
			buf.erase( remove_if( buf.begin(), buf.end(), ::isspace ), buf.end() );

			end = 0;

			temp.clear();
			temp.resize(gene_length, 0);

			// go till the last delimiter is found
			while(true)
			{
				// find the next delimiter
				end = buf.find(";");

				if (end == string::npos)
					break;

				// extract the data till the delimiter
				data = buf.substr(0, end);

				// the postiion of the placed amplifier
				cand_location_id = stoi(data);

				// no overflow
				if (!BINARY_INIT_INPUT)
				{
					if (cand_location_id >= gene_length)
					{
						cout << "Gene length: " << gene_length << endl;
						throw invalid_argument("Candidate location id is out of range");
					}
				}

				else if (BINARY_INIT_INPUT)
				{
					if (cand_location_id != 0 && cand_location_id != 1)
						throw invalid_argument("Candidate location input is set as binary");

					if (amp_counter == gene_length)
						throw invalid_argument("Candidate location input out of range");
				}

				// cut the processed part of the string
				buf = buf.substr(end + 1);

				// place the amp
				if (!BINARY_INIT_INPUT)
					temp[cand_location_id] = 1;
					
				else
				{
					temp[amp_counter] = cand_location_id;
					amp_counter ++;
				}
			}
			population[init_placement_num] = GA_Solution_OA(chromosome_struct, temp, permutable);

			LogFile << endl << "Initial placement: ";
			population[init_placement_num].print(LogFile, 0);
			LogFile << endl;

			LogFile << " with cost " << " placed as member " << init_placement_num << endl;
		}

		InitFile.close();
	}

	else if(current_mode == Tree_Establishment_single || current_mode == Tree_Establishment_multi)
	{
		// read the file with the initial placements
		ifstream InitFile(INIT_FILE_NAME_TE, ios::in);

		if (!InitFile.is_open())
			throw ifstream::failure("Failed to open the init file" + string(INIT_FILE_NAME_TE));

		int link_counter;
		int start, end;
		string buf, data;
		string s_init_placement = "Initial establishment";

		int init_placement_num, tree_id;
		vector<int>temp;


		while(!InitFile.eof())
		{
			// first line
			getline(InitFile, buf);

			// if it's commented, skip
			if (buf.find("//") != -1)
				continue;

			// skip the title
			start = buf.find(s_init_placement);
			if (start == string::npos)
				continue;

			// read the number and get rid of the spaces
			data = buf.substr(start + s_init_placement.length());
			data.erase( remove_if( data.begin(), data.end(), ::isspace ), data.end() );

			// the number of the members in the population
			init_placement_num = stoi(data);

			// no overflow
			if (init_placement_num >= population_size)
				throw invalid_argument("Initial establishment is out of range");

			link_counter = 0;

			// second line
			getline(InitFile, buf);

			// extract the id list from the brackets
			start = buf.find("<");
			end = buf.find(">");

			if (start == string::npos || end == string::npos)
				continue;

			buf = buf.substr(start + 1, end - start - 1);

			// delete the spaces
			buf.erase( remove_if( buf.begin(), buf.end(), ::isspace ), buf.end() );

			end = 0;

			temp.clear();
			temp.resize(gene_length, 0);

			// go till the last delimiter is found
			while(true)
			{
				// find the next delimiter
				end = buf.find(";");

				if (end == string::npos)
					break;

				// extract the data till the delimiter
				data = buf.substr(0, end);

				// the postiion of the placed amplifier
				tree_id = stoi(data);

				if(tree_id >= chromosome_struct[0].get_size())
					throw invalid_argument("Tree id is out of range");

				// cut the processed part of the string
				buf = buf.substr(end + 1);

				temp[link_counter] = tree_id;
				link_counter ++;
			}

			population[init_placement_num] = GA_Solution_OA(chromosome_struct, temp, permutable);

			LogFile << endl << "Initial establishment: ";
			population[init_placement_num].print(LogFile, 2);
			LogFile << endl;

			LogFile << " placed as member " << init_placement_num << endl;
		}

		InitFile.close();
	}

	return 0;
}


int GeneticAlgorithm_OA :: find_unique_solutions(vector<int>& matching_list)
{
	unique_solutions.clear();

	unordered_set<GA_Solution_OA, GA_Solution_OA::HashFunction> s;

	for (int i = 0; i < population_size; i ++)
	{
		auto temp = s.insert(population[i]);

		if (temp.second == true)
		{
			unique_solutions.push_back(population[i]);
			matching_list.push_back(unique_solutions.size() - 1);
		}

		else
		{
			vector<GA_Solution_OA>::iterator it = find(unique_solutions.begin(), unique_solutions.end(), population[i]);
        	
			if(it == unique_solutions.end())
				throw runtime_error("Unique but not unique");
			
			int ind = it - unique_solutions.begin();

			matching_list.push_back(ind);
		}
	}

	if (unique_solutions.size() == 0)
		throw runtime_error("There should be at least 1 unique solution in the population");

	return unique_solutions.size();
}


int GeneticAlgorithm_OA :: next_generation(vector<float>& feasibility, vector<vector<float>>& fitness_values)
{
	//auto t0 = std::chrono::high_resolution_clock::now();

	if (current_mode == Tree_Establishment_single || current_mode == Tree_Establishment_multi)
		process_feasible_solutions(feasibility, fitness_values);

	/*auto t1 = std::chrono::high_resolution_clock::now();
	auto duration = std::chrono::duration_cast<std::chrono::microseconds>( t1 - t0 ).count();
    std::cout << "Process feasible, mks: " << duration << endl;*/

	// find the best solutions in this generation and perform hetacomb if needed
	fitness_calculation(feasibility, fitness_values);

	/*auto t2 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t2 - t1 ).count();
    std::cout << "Fitness, mks: " << duration << endl;*/

	// for multiobjective GA - divide the population into Pareto fronts and assign ranks based on front numbers
	if (feasible_found && (current_mode == OA_placement_multi || current_mode == Tree_Establishment_multi || current_mode == RSA_multi) )
		ranking(feasibility, fitness_values);

	// select members for the tournament
	vector<int> order_ind = preselection(feasibility, fitness_values);

	/*auto t3 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t3 - t2 ).count();
    std::cout << "Preselection, mks: " << duration << endl;*/

	// compare solutions by their fitness and feasibilities
	vector<int> selected_ind = tournament_selection(feasibility, order_ind, fitness_values);

	/*auto t4 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t4 - t3 ).count();
    std::cout << "Tournament, mks: " << duration << endl;*/

	crossover(selected_ind);

	/*auto t5 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t5 - t4 ).count();
    std::cout << "Crossover, mks: " << duration << endl;*/

	// mutation
	mutation(selected_ind.size());

	/*auto t6 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t6 - t5 ).count();
    std::cout << "Mutation, mks: " << duration << endl;*/
	
	// fill the population to the original size
	recreate_population(selected_ind.size());

	/*auto t7 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t7 - t6 ).count();
    std::cout << "Recreate, mks: " << duration << endl;*/

	// tweak the probability distribution of the number of mutations happening
	change_mutation_pattern();

	/*auto t8 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t8 - t7 ).count();
    std::cout << "Change mutation, mks: " << duration << endl << endl;*/

	// if(gen_in_current_state > 10)
	// 	switch_state(finish_state);

	if(fast_run)
	{
		if (!feasible_found && (current_mode == RSA_single || current_mode == Ordering) && (generation_num > 20) )
			switch_state(finish_state);

		else if (feasible_found && (current_mode == RSA_single || current_mode == Ordering) && generation_num > 20)
			switch_state(finish_state);

		else if (current_mode != RSA_single && (generation_num - gen_best_cost > 5 || generation_num > 15) )
			switch_state(finish_state);
	}

	else
	{
		// finish
		if (feasible_found && current_state == stuck_state)
		{
			if (current_mode == Tree_Establishment_single || current_mode == Tree_Establishment_multi)
			{
				if(gen_in_current_state > 50) //gene_length * 5)
					switch_state(finish_state);
			}

			else
			{
				if(generation_num - gen_best_cost > 50)
					//gen_in_current_state > 10)
					//gen_in_current_state > (int)(gene_length * 2) )
					switch_state(finish_state);
			}
		}
			
		else if (feasible_found == false && current_state == stuck_state)
		{
			if (current_mode == OA_placement_single || current_mode == OA_placement_multi)
			{
				if(gen_in_current_state > (int)gene_length * 50)
					switch_state(finish_state);
			}

			else
			{
				if(generation_num - gen_best_feasibility_val > 500)//gene_length * 2)
				//gen_in_current_state > 25)
					switch_state(finish_state);
			}
		}
	}

	generation_num ++;
	gen_in_current_state ++;

	return 0;
}


int GeneticAlgorithm_OA :: switch_state(State new_state)
{
	current_state = new_state;
	
	gen_in_current_state = 0;

	if(fast_run == false)
		LogFile << endl << "**** State changed to ";
	
	switch (new_state)
	{
		case active_state:
			if(fast_run == false)
				LogFile << "active state";
			
			row_of_mutation_matrix = round(gene_length * RATIO_OF_GENES_MUTATED_INIT);

			if (row_of_mutation_matrix < 3)
				row_of_mutation_matrix = 3;

			row_of_mutation_matrix --;

			hetacomb_counter = 0;

			break;

		case stuck_state:
			if(fast_run == false)
				LogFile << "stuck state";

			gen_before_hetacomb = 0;
			row_of_mutation_matrix = 1;
			break;

		case finish_state:
			if(fast_run == false)
				LogFile << " finish state";
			break;
	}

   	if(fast_run == false)
		LogFile << "****" << endl;

	return 0;
}


int GeneticAlgorithm_OA :: process_feasible_solutions(vector<float>& feasibility, vector<vector<float>>& fitness_values)
{
	// look for the new best solutions
	for (int sol_ind = 0; sol_ind < population.size(); sol_ind ++)
	{
		if(feasibility[sol_ind] < 1)
			continue;

		// check if it was saved before
		auto solution = feasible_solutions.find(population[sol_ind]);

		// save the new value
		if(solution == feasible_solutions.end())
		{
			//cout << "Solution with fitness " << fitness_values[0][sol_ind] << " is saved " << endl;
			
			population[sol_ind].set_cost(fitness_values[0][sol_ind]);
			feasible_solutions.insert(population[sol_ind]);
		}

		// update the existing value if the new solution has lower fitness
		// (this happens if the same establishment was processed in the earlier generation and gave a higher cost)
		else if (solution != feasible_solutions.end() && fitness_values[0][sol_ind] < (*solution).get_cost())
		{
			//cout << "Solution with fitness " << (*solution).get_cost() << " is updated with fitness " << fitness_values[0][sol_ind] << endl;
			/*population[sol_ind].print(ObjFile, 2);
			ObjFile << endl;*/

			(*solution).set_cost(fitness_values[0][sol_ind]);

			// update the fitness of the same solutions before this one
			// if there will be solutions after this one
			for(int prev_solution = 0; prev_solution < sol_ind; prev_solution ++)
			{
				if(population[prev_solution] == population[sol_ind] and fitness_values[0][prev_solution] > fitness_values[0][sol_ind])
				{
					fitness_values[0][prev_solution] = fitness_values[0][sol_ind];
					
					// if it is lower than before, it is feasible
					feasibility[prev_solution] = 1;
				}
			}
		}

		// if a solution has a higher fitness than the saved one, update it
		// (this happens if the same establishment is processed in the further thread than the best found one)
		else if(solution != feasible_solutions.end() && fitness_values[0][sol_ind] > (*solution).get_cost())
			fitness_values[0][sol_ind] = (*solution).get_cost();

		if(fitness_values[0][sol_ind] == 1e6)
			feasibility[sol_ind] = 0.997;
	}

	return 0;
}


pair<bool, float> GeneticAlgorithm_OA :: find_feasible_solution(int solution_ind)
{
	auto solution = feasible_solutions.find(unique_solutions[solution_ind]);
	
	if (solution == feasible_solutions.end())
		return {false, 1e6};

	else
		return {true, (*solution).get_cost()};
}


int GeneticAlgorithm_OA :: fitness_calculation(vector<float>& feasibility, vector<vector<float>>& fitness_values)
{
	// check whether there are feasible solutions
	// (required if all feasible ones were deleted in the hecatomb at the previous generation)
	float max_feas = 0;
		
	for (int i = 0; i < population_size; i ++)
		if(feasibility[i] > max_feas)
			max_feas = feasibility[i];

	if (max_feas != 1.0 && feasible_found == true)
	{
		feasible_found = false;

		LogFile << "No feasible solutions present anymore" << endl;

		// any feasible solutions will be saved from now on, but only new ones (best_solutions_feasible isn't cleared)
		best_cost = 1e6;
		best_feasibility_val = max_feas - 1e-3;
		gen_best_feasibility_val = generation_num;
	}

	
	// for debugging only
	map<float, int> cost_distribution;
	map<float, int> feasibility_distribution;

	current_best_cost = INIT_FIT_VALUE;
	current_best_feasibility = 0;


	// look for the new best solutions
	for (int i = 0; i < population_size; i ++)
	{
		// calculate the distribution of feasibilities
		if (feasible_found == false)
		{
			feasibility_distribution[feasibility[i]] ++;

			if (feasibility[i] > current_best_feasibility)
				current_best_feasibility = feasibility[i];
		}

		else if (feasible_found && feasibility[i] == 1.0)
		{
			cost_distribution[(int)round(fitness_values[0][i])] ++;

			// save the current best primary fitness
			// used to start a hetacomb if we are close to the current optimum
			if (fitness_values[0][i] < current_best_cost)
				current_best_cost = fitness_values[0][i];
		}


		// proceed to saving the new best solutions
		if (feasibility[i] == 1.0 && fitness_values[0][i] < (best_cost + fabs(best_cost) * RATIO_CLOSE_TO_OPTIMUM) && 
			best_solutions_feasible.find(population[i]) == best_solutions_feasible.end() )
		{
			// primary fitness minimization is the main goal
			// if a new solution is smaller or equal
			if (fitness_values[0][i] <= best_cost + EPS)
			{
				// strictly smaller than the current best
				if (fitness_values[0][i] < best_cost - EPS)
				{
					if(fast_run == false)
					{
						if (current_mode == Ordering || current_mode == OA_placement_single || current_mode == Tree_Establishment_single || current_mode == RSA_single)
							LogFile << endl << "New best solution found at generation " << generation_num << " with a obj " << fitness_values[0][i] << endl;
									
						else if (current_mode == OA_placement_multi || current_mode == RSA_multi)
							LogFile << endl << "New best solution found at generation " << generation_num << " with a obj_1 " << fitness_values[0][i] << " and obj_2 " << fitness_values[1][i] << endl;

						if (current_mode == OA_placement_single or current_mode == OA_placement_multi)
							population[i].print(LogFile, 0);

						else if(current_mode == Tree_Establishment_single)
							population[i].print(LogFile, 2);

						LogFile << endl;
					}

					// unfeasible results are cleared
					if (feasible_found == false)
					{
						feasible_found = true;

						best_feasibility_val = 1.0;
						best_solutions_unfeasible.clear();

						current_best_cost = fitness_values[0][i];
						cost_distribution[(int)round(fitness_values[0][i])] ++;
					}

					// switch the state to active
					if (current_state == stuck_state)
						switch_state(active_state);

					// save the solution
					best_cost = fitness_values[0][i];
					gen_best_cost = generation_num;

					// tweak the margin
					best_cost_margin = RATIO_BEST_FIT_MARGIN_MIN * fabs(best_cost);
				
					if(current_mode == RSA_multi)
						best_solutions_feasible.clear();
				}
					
				// save the new best solution
				best_solutions_feasible.insert(population[i]);
			}
		}

		// no feasible solution yet, with equal or bigger feasibility, new
		else if (feasible_found == false && feasibility[i] != 0 && feasibility[i] > (best_feasibility_val - EPS) && 
			best_solutions_unfeasible.find(population[i]) == best_solutions_unfeasible.end())
		{
			// with a strictly better feasibility
			if (feasibility[i] > best_feasibility_val + EPS)
			{
				if(fast_run == false)
				{
					LogFile << endl << "Solution closer to feasible found at generation " << generation_num << " with feasibility " << feasibility[i] << endl;
					population[i].print(LogFile, 2);
					LogFile << endl;
				}

				// save it
				best_feasibility_val = feasibility[i];
				gen_best_feasibility_val = generation_num;

				if (current_mode == RSA_single || current_mode == RSA_multi || current_mode == OA_placement_single || current_mode == OA_placement_multi)
				{
					// tweak the margin
					if (best_feasibility_val < 0.7)
						best_feasibility_margin = 0.1;

					else if (best_feasibility_val > 0.7 && best_feasibility_val < 0.9)
						best_feasibility_margin = 0.05;
					
					else if (best_feasibility_val >= 0.9 && best_feasibility_val < 0.97)
						best_feasibility_margin = 0.01;

					else if (best_feasibility_val >= 0.97)
						best_feasibility_margin = 0.005;
				}

				else
					best_feasibility_margin = 0.01;
			}

			// save it to the solutions with the same feasibility
			best_solutions_unfeasible.insert(population[i]);
		}
	}


	// switch the state if no improvement
	if ( (feasible_found && current_state == active_state && (generation_num - gen_best_cost) > GEN_BEFORE_BEING_STUCK) ||
			(feasible_found == false && current_state == active_state && (generation_num - gen_best_feasibility_val) > GEN_BEFORE_BEING_STUCK) )
		switch_state(stuck_state);


    // delete the best solutions in the current generation if needed
	//if (current_mode != RSA_single && current_mode != RSA_multi)
    	//hetacomb(cost_distribution, feasibility_distribution, feasibility, fitness_values);

	// output the distribution of costs for fesible solutions in the population
	if (fast_run == false && VERBOSE_DEBUG)
	{
		if(feasible_found)
		{
			LogFile << endl;
			for (auto map_it = cost_distribution.begin(); map_it != cost_distribution.end(); map_it++)
			{
				LogFile << map_it -> first << " : ";
				
				for (int j = 0; j < map_it -> second; j ++)
					LogFile << "*";

				LogFile << endl;
			}	
			LogFile << endl;
		}

		else
		{
			LogFile << endl;
			for (auto feasibilty_map_it = feasibility_distribution.begin(); feasibilty_map_it != feasibility_distribution.end(); feasibilty_map_it++)
			{
				LogFile << feasibilty_map_it -> first << " : ";
				
				for (int j = 0; j < feasibilty_map_it -> second; j ++)
					LogFile << "*";

				LogFile << endl;
			}	
			LogFile << endl;			
		}
		
	}

	if(fast_run == false)
		cout << "Best fitness value at gen " << generation_num << " since gen " << gen_best_cost << " is " << best_cost << endl;
	return 0;
}


int GeneticAlgorithm_OA ::hetacomb(map<float, int>& cost_distribution, map<float, int>& feasibility_distribution, vector<float>& feasibility, vector<vector<float>>& fitness_values)
{
    if (current_state == stuck_state && gen_before_hetacomb != 0)
		gen_before_hetacomb --;


    	// delay or force the hetacomb 
	if (feasible_found && current_state == stuck_state)
	{
		// find the cost with the most solutions in the population
		auto map_it = std::max_element(cost_distribution.begin(), cost_distribution.end(),[] 
		(const pair<float,int>& a, const pair<float,int>& b)
		{ 
			return a.second < b.second;
		} );

		// force the hetacomb if there are too many (> 40) solutions with current min cost
		// and we are halfway to the hetacomb because
		// most of them aren't unique but they fill the population
    	if (distance(cost_distribution.begin(), map_it) < 2 && map_it -> second > 40 && gen_before_hetacomb < GEN_BEFORE_BEING_STUCK / 2)
			gen_before_hetacomb = 0;

		// or delay it if there are too little (< 10) solutions with current min cost
		if (gen_before_hetacomb == 0 && cost_distribution.begin() -> second < 10)
			gen_before_hetacomb += 5;

		// or if there is no variety of solutions 
		// doesn't work for TE, as there are always few solutions in TE
		if (current_mode != Tree_Establishment_single && gen_before_hetacomb == 0 && cost_distribution.size() < 10)
			gen_before_hetacomb += 10;

		if (fast_run == false && VERBOSE_DEBUG)
			LogFile << endl << gen_before_hetacomb << " before the next hetacomb" << endl;
	}

	else if (!feasible_found && current_state == stuck_state)
	{
		// find the feasibility with the most solutions in the population
		auto map_it = std::max_element(feasibility_distribution.begin(), feasibility_distribution.end(),[] 
		(const pair<int,int>& a, const pair<int,int>& b)
		{ 
			return a.second < b.second;
		} );

		// force the hetacomb if there are too many (> 40) solutions with current min cost
		// and we are halfway to the hetacomb because
		// most of them aren't unique but they fill the population
    	if (distance(map_it, feasibility_distribution.end()) < 2 && map_it -> second > 20)// && gen_before_hetacomb < GEN_BEFORE_BEING_STUCK / 2)
			gen_before_hetacomb = 0;

		// or delay it if there are too little (< 10) solutions with current min cost
		//if (gen_before_hetacomb == 0 && feasibility_distribution.end() -> second < 5)
		//	gen_before_hetacomb += 5;

		// or if there is no variety of solutions 
		// doesn't work for TE, as there are always few solutions in TE
		if (current_mode != Tree_Establishment_single && gen_before_hetacomb == 0 && feasibility_distribution.size() < 5)
			gen_before_hetacomb += 10;

		if (fast_run == false && VERBOSE_DEBUG)
			LogFile << endl << gen_before_hetacomb << " before the next hetacomb" << endl;
	}


    // need to pass this to the GA_Solution to compare different tree etablishments properly
    bool permutable = false;

    if(current_mode == Tree_Establishment_single || current_mode == Tree_Establishment_multi)
        permutable = true;

	
	// delete the best solutions of the population and fill them with random ones
	if (current_state == stuck_state && gen_before_hetacomb == 0)
	{
		// if we are close enough to the local optimum, get rid of the current best solutions
		if (feasible_found && current_best_cost < best_cost + 1)
		{
			best_cost_margin = 1;//0.05 * (hetacomb_counter / 2.0) * best_cost;

			int count = 0;

			for(int i = 0; i < population_size; i ++)
			{
				if(fitness_values[0][i] - best_cost < best_cost_margin)
				{
					population[i] = GA_Solution_OA(chromosome_struct, permutable);

					count ++;
				}
			}

			gen_before_hetacomb = GEN_BEFORE_BEING_STUCK + 2 * hetacomb_counter;

			if (hetacomb_counter < max_hetacomb_counter)
				hetacomb_counter ++;

			if (fast_run == false && VERBOSE_DEBUG)
			{
				LogFile << count << " solutions lower than " << best_cost + best_cost_margin << " deleted" << endl;
				LogFile << gen_before_hetacomb << " generations before the next hetacomb" << endl;

				if (hetacomb_counter == max_hetacomb_counter)
					LogFile << endl << "No more increase in hecatomb margin after " << best_cost_margin << endl;
			}

			best_cost_margin = fabs(best_cost) * RATIO_BEST_FIT_MARGIN_MIN;
		}

		// only for OA placement, as finding a feasible solution in TE and RSA is very hard
		else if (!feasible_found && current_best_feasibility == best_feasibility_val && current_mode != Tree_Establishment_single)
		{
			int count = 0;

			best_feasibility_margin = 0.01 + 0.02;// * hetacomb_counter;

			for(int i = 0; i < population_size; i ++)
			{
				if(best_feasibility_val - feasibility[i] < best_feasibility_margin)
				{
					population[i] = GA_Solution_OA(chromosome_struct, permutable);

					count ++;
				}
			}

			best_feasibility_margin = 0.02;
			gen_before_hetacomb = GEN_BEFORE_BEING_STUCK;

			if (hetacomb_counter < max_hetacomb_counter)
				hetacomb_counter ++;

			if (fast_run == false && VERBOSE_DEBUG)
			{
				LogFile << count << " solutions with feasibility higher than " << best_feasibility_val - 2 * best_feasibility_margin << " deleted" << endl;
				LogFile << gen_before_hetacomb << " generations before the next hetacomb" << endl;

				if (hetacomb_counter == max_hetacomb_counter)
					LogFile << endl << "No more increase in hecatomb margin" << endl;
			}
		}

		else
		{
			if (fast_run == false && VERBOSE_DEBUG)
				LogFile << "Too far from the local optimum to perform elimination: " << best_feasibility_val << endl;
		}
	}

    return 0;
}


int GeneticAlgorithm_OA :: ranking(vector<float>& feasibility, vector<vector<float>>& fitness_values)
{
	int num_objectives = fitness_values.size();
	int feasible_count;		// feasible solutions in the front


	// how many feasible solutions will be in the first class during preselection
	int opt_front_size = 50;

	if (current_state == stuck_state)
		opt_front_size = 50;

	// best feasible solutions from the first fronts in this generation
	vector<int> current_opt_front_ind;


	// two values to be compared
	vector<float> one, two;

	bool one_is_dominated;

	int counter = 0;	// members with already defined rank

	int current_front_num = 1;
	
	// indexes of members with current_front_num
	vector<int> current_front_ind;
	

	// reset assignments to fronts
	for (int i = 0; i < population_size; i ++)
	{
		front_number[i] = 0;
		crowding_distances[i] = 0;
	}
	
	// values that describe the distribution of solutions among the fronts
	first_feasible_front_ind = -1;
	middle_feasible_front_ind = -1;
	last_opt_front_ind = -1;


	// till all the members are distributed into fronts
	while(counter != population_size)
	{
		current_front_ind.clear();
		feasible_count = 0;

		// find non-dominated solutions in the population
		for (int i = 0; i < population_size; i ++)
		{
			// if this solution is already assigned to a front
			if (front_number[i] != 0)
				continue;

			// if the solution is unfeasible
			if (feasible_found && feasibility[i] < 0.75)
			{
				front_number[i] = 10000;
				counter ++;
				continue;
			}

			// prepare the objective vector
			one.clear();
			for (int obj = 0; obj < num_objectives; obj ++)
				one.push_back(fitness_values[obj][i]);

			one_is_dominated = false;

			// compare member i with other remaining members of the population
			for (int j = 0; j < population_size; j ++)
			{
				// if it has been already assigned a front
				if (i == j || front_number[j] != 0)
					continue;
				
				// if the solution is unfeasible
				if (feasible_found && feasibility[j] < 0.75)
				{
					front_number[j] = 10000;
					counter ++;
					continue;
				}

				// prepare the objective vector 
				two.clear();
				for (int obj = 0; obj < num_objectives; obj ++)
					two.push_back(fitness_values[obj][j]);

				// check if i is dominated by j
				if (dominates(two, one))
				{
					one_is_dominated = true;
					break;
				}
			}

			// if one isn't dominated by any reamining members of the population
			// assign it to the front
			if (one_is_dominated == false)
			{
				current_front_ind.push_back(i);

				counter ++;

				// if the solution is feasible
				if (feasibility[i] == 1.0)
				{
					feasible_count ++;

					// if the list of feasible solutions from first fronts isn't full
					if (current_opt_front_ind.size() < opt_front_size && 
						find_if(current_opt_front_ind.begin(), current_opt_front_ind.end(), [this, i] (const int index) 
						{
							return population[i] == population[index];
						} ) == current_opt_front_ind.end())
					{
						current_opt_front_ind.push_back(i);
					}

					// if it's the current optimal cost
					if (fitness_values[0][i] < current_best_cost + EPS)
						last_opt_front_ind = current_front_num;
				}
			}
		}

		// assign the rank
		for(int i = 0; i < current_front_ind.size(); i ++)
			front_number[current_front_ind[i]] = current_front_num;

		if (first_feasible_front_ind == -1 && feasible_count)
			first_feasible_front_ind = current_front_num;

		if (current_opt_front_ind.size() >= opt_front_size && middle_feasible_front_ind == -1)
		{
			middle_feasible_front_ind = current_front_num;

			if (feasible_count > opt_front_size && middle_feasible_front_ind > first_feasible_front_ind)
				middle_feasible_front_ind --;
		}

		current_front_num ++;
	}

	max_front_num = current_front_num - 1;


	// reduce the number of fronts to around MAX_FRONT_NUM
	if (max_front_num > 2 * MAX_FRONT_NUM - 1)
	{
		int mult = max_front_num / MAX_FRONT_NUM;
		int res = max_front_num % MAX_FRONT_NUM;

		int short_front_num = 1;

		for(int i = 0; i < max_front_num - res; i += mult)
		{
			current_front_ind.clear();

			for(int j = 0; j < population_size; j ++)
			{
				if (front_number[j] == 10000)
					continue;

				else if (front_number[j] >= i && front_number[j] < i + mult)
				{
					front_number[j] = short_front_num;
					current_front_ind.push_back(j);
				}

				// also recompute the values of the front descriptors
				if (first_feasible_front_ind > i && first_feasible_front_ind <= i + mult)
					first_feasible_front_ind = short_front_num;
				
				if (middle_feasible_front_ind > i && middle_feasible_front_ind <= i + mult)
					middle_feasible_front_ind = short_front_num;

				if (last_opt_front_ind > i && last_opt_front_ind <= i + mult)
					last_opt_front_ind = short_front_num;
			}

			crowding_distance_computation(current_front_ind, fitness_values);
			short_front_num ++;
		}

		current_front_ind.clear();

		// combine the remaining fronts into one
		for(int i = max_front_num - res; i < max_front_num + 1; i ++)
		{
			for(int j = 0; j < population_size; j ++)
			{
				if (front_number[j] == 10000)
					continue;

				else if (front_number[j] == i)
				{
					front_number[j] = short_front_num;
					current_front_ind.push_back(j);
				}

				if (first_feasible_front_ind == i)
					first_feasible_front_ind = short_front_num;

				if (middle_feasible_front_ind == i)
					middle_feasible_front_ind = short_front_num;

				if (last_opt_front_ind == i)
					last_opt_front_ind = short_front_num;
			}
		}

		crowding_distance_computation(current_front_ind, fitness_values);
		max_front_num = short_front_num;
	}

	// if there aren't enough feasible solutions
	if (first_feasible_front_ind != -1 && middle_feasible_front_ind == -1)
		middle_feasible_front_ind = max_front_num;

	if (fast_run == false && VERBOSE_DEBUG)
	{
		LogFile << endl << "First feasible front: " << first_feasible_front_ind << endl;
		LogFile << "Middle feasible front: " << middle_feasible_front_ind << endl;
		LogFile << "Last front with an current optimal solution: " << last_opt_front_ind << endl;
		LogFile << "Max front: " << max_front_num << endl;
	}

	// output the feasible solutions from the first fronts
	/*if (fast_run == false && VERBOSE_DEBUG && current_opt_front_ind.size() != 0)
	{
		// output the best feasible solutions from the front fronts
		ObjFile << generation_num << endl;
		ObjFile << current_opt_front_ind.size() << endl;

		for(int i = 0; i < num_objectives; i ++)
		{
			for(int j = 0; j < current_opt_front_ind.size(); j ++)
				ObjFile << fitness_values[i][current_opt_front_ind[j]] << " ";
			
			ObjFile << endl;
		}
	}*/

	return 0;
}


int  GeneticAlgorithm_OA :: crowding_distance_computation(vector<int>& front_ind, vector<vector<float>>& fitness_values)
{
	int num_objectives = fitness_values.size();

	vector<int> unique_front_ind;	// indexes of members with current_front_num and unique fitnesses

	// max values of fitness values in the front
	vector<float> max_front_fit_val(num_objectives);
	vector<float> min_front_fit_val(num_objectives);
	float crowding_distance_temp;


	for (int obj = 0; obj < num_objectives; obj ++)
	{
		max_front_fit_val[obj] = -INIT_FIT_VALUE;
		min_front_fit_val[obj] = INIT_FIT_VALUE;
	}

	// find the max and min values of the objectives
	for(int j = 0; j < front_ind.size(); j ++)
	{
		// check if it's a max or min value of the front
		for (int obj = 0; obj < num_objectives; obj ++)
		{
			if (fitness_values[obj][front_ind[j]] < min_front_fit_val[obj])
				min_front_fit_val[obj] = fitness_values[obj][front_ind[j]];

			else if (fitness_values[obj][front_ind[j]] > max_front_fit_val[obj])
				max_front_fit_val[obj] = fitness_values[obj][front_ind[j]];
		}
	}

	// compute the crowding distances
	for (int obj = 0; obj < num_objectives; obj ++)
	{
		// extract the unique indexes with respect to obj
		unique_front_ind = front_ind;

		// sort the indexes from smallest to largest according to obj 	
		sort(unique_front_ind.begin(), unique_front_ind.end(), [&](const int first, const int second) 
		{
			return fitness_values[obj][first] < fitness_values[obj][second];
		});

		unique_front_ind.erase( unique( unique_front_ind.begin(), unique_front_ind.end(), [&] (const int one, const int two)
		{
			return fitness_values[obj][one] == fitness_values[obj][two];
		} ), unique_front_ind.end() );


		// calculate the crowding distances
		for(int j = 0; j < unique_front_ind.size(); j ++)
		{
			// if it's the first or the last member of the front
			if (j == 0 || j == unique_front_ind.size() - 1)
				crowding_distance_temp = 1000.0;

			else
				crowding_distance_temp = (fitness_values[obj][unique_front_ind[j + 1]] - fitness_values[obj][unique_front_ind[j - 1]]) / (max_front_fit_val[obj] - min_front_fit_val[obj]);


			// assign the crowding distance to all the solutions with the same fitness value
			for (int k = 0; k < front_ind.size(); k ++)
			{
				if (fitness_values[obj][unique_front_ind[j]] == fitness_values[obj][front_ind[k]])
					crowding_distances[front_ind[k]] += crowding_distance_temp;
			}
		}
	}

	return 0;
}


bool GeneticAlgorithm_OA :: dominates(vector<float>& one, vector<float>& two)
{
	if (one.size() != two.size())
		throw invalid_argument("Vectors of fitness have to be of the same length");

	bool one_dominates_two = false;

	for (int i = 0; i < one.size(); i ++)
	{
		if (one[i] > two[i])
		{
			one_dominates_two = false;
			break;
		}

		if (one[i] < two[i])
			one_dominates_two = true;
	}

	return one_dominates_two;
}


vector<int> GeneticAlgorithm_OA :: preselection(vector<float>& feasibility, vector<vector<float>>& fitness_values)
{
	// create 3 groups: 
	// feasible, first fronts
	// feasible, middle fronts
	// infeasible, cost around the current best
	vector<int> first_class_ind;
	vector<int> second_class_ind;
	vector<int> third_class_ind;

	unordered_set<GA_Solution_OA, GA_Solution_OA::HashFunction> first_class;
	unordered_set<GA_Solution_OA, GA_Solution_OA::HashFunction> second_class;


	if (feasible_found && (current_mode == RSA_multi || current_mode == OA_placement_multi || current_mode == Tree_Establishment_multi) )
	{
		int first_margin = middle_feasible_front_ind;
		int second_margin = last_opt_front_ind;

		// if they are too close
		if (last_opt_front_ind < middle_feasible_front_ind + 10)
			second_margin = middle_feasible_front_ind + 0.5 * (max_front_num - middle_feasible_front_ind);

		
		// distribute the solutions into groups
		for (int i = 0; i < population_size; i ++)
		{
			if (feasibility[i] == 1.0 && front_number[i] <= first_margin &&
				find_if(first_class_ind.begin(), first_class_ind.end(), [this, i] (const int index) 
				{
						return population[i] == population[index];
				} ) == first_class_ind.end())
			{
				first_class_ind.push_back(i);
			}

			else if (feasibility[i] == 1.0 && front_number[i] <= second_margin && 
				fitness_values[0][i] < current_best_cost + best_cost_margin &&
				find_if(second_class_ind.begin(), second_class_ind.end(), [this, i] (const int index) 
				{
						return population[i] == population[index];
				} ) == second_class_ind.end())
			{
				second_class_ind.push_back(i);
			}

			else if (fitness_values[0][i] < current_best_cost + 2*best_cost_margin && 
				find_if(third_class_ind.begin(), third_class_ind.end(), [this, i] (const int index) 
				{
						return population[i] == population[index];
				} ) == third_class_ind.end())
			{
				third_class_ind.push_back(i);
			}
		}
	}

	else if (feasible_found && (current_mode == Ordering || current_mode == RSA_single || current_mode == OA_placement_single || current_mode == Tree_Establishment_single) )
	{
		// distribute the solutions into groups
		for (int i = 0; i < population_size; i ++)
		{
			if (feasibility[i] == 1.0 && 
				fitness_values[0][i] < current_best_cost + fabs(current_best_cost) * RATIO_BEST_FIT_MARGIN_MIN &&
				first_class.find(population[i]) == first_class.end())
			{
				first_class_ind.push_back(i);
				first_class.insert(population[i]);
			}

			else if (feasibility[i] == 1.0 && 
				fitness_values[0][i] < current_best_cost + fabs(current_best_cost) * RATIO_BEST_FIT_MARGIN_MAX &&
				second_class.find(population[i]) == second_class.end())
			{
				second_class_ind.push_back(i);
				second_class.insert(population[i]);
			}

			else if (current_mode == OA_placement_single && feasibility[i] >= 0.95)
				third_class_ind.push_back(i);

			else if (current_mode == Tree_Establishment_single && feasibility[i] == 1.0)
				third_class_ind.push_back(i);

			else if ( current_mode == RSA_single && feasibility[i] == 1.0 && third_class_ind.size() < 50)
				third_class_ind.push_back(i);
		}
	}

	// no feasible solution found yet
	else if (feasible_found == false && (current_mode == Ordering || current_mode == RSA_single || current_mode == RSA_multi || current_mode == OA_placement_single || current_mode == OA_placement_multi) )
	{
		// distribute the solutions into groups
		for (int i = 0; i < population_size; i ++)
		{
			// slightly worse than the current best feasibility
			if (first_class_ind.size() < 250 && feasibility[i] > current_best_feasibility - best_feasibility_margin && 
				first_class.find(population[i]) == first_class.end())
			{
				first_class_ind.push_back(i);
				first_class.insert(population[i]);
			}

			else if (second_class_ind.size() < 500 && feasibility[i] > current_best_feasibility - 1.5 * best_feasibility_margin &&
				second_class.find(population[i]) == second_class.end())
			{
				second_class_ind.push_back(i);
				second_class.insert(population[i]);
			}

			else if (third_class_ind.size() < 1000)
				third_class_ind.push_back(i);
		}
	}

	// no feasible solution found yet
	else if (feasible_found == false && (current_mode == Tree_Establishment_single || current_mode == Tree_Establishment_multi) )
	{
		// distribute the solutions into groups
		for (int i = 0; i < population_size; i ++)
		{
			// slightly worse than the current best feasibility
			if (feasibility[i] > current_best_feasibility - best_feasibility_margin)
				first_class_ind.push_back(i);

			else if (feasibility[i] > current_best_feasibility - 2 * best_feasibility_margin)
				second_class_ind.push_back(i);

			else if(feasibility[i] != 0)
				third_class_ind.push_back(i);
		}
	}

	if (fast_run == false && VERBOSE_DEBUG)
	{
		LogFile << endl << first_class_ind.size() << " solutions in first class" << endl;
		LogFile << second_class_ind.size() << " solutions in second class" << endl;
		LogFile << third_class_ind.size() << " solutions in third class" << endl;
	}

	
    // if we've managed to delete all the feasible solutions during the hetacomb
	// fill the classes with random solutions and if needed perform elitism later while recreating the new population
	if (first_class_ind.size() == 0 && second_class_ind.size() == 0 && third_class_ind.size() == 0)
	{
		for (int i = 0; i < 50; i ++)
			first_class_ind.push_back(rand() % population_size);

		current_best_cost = INIT_FIT_VALUE;
	}


	// select part of the next population
	float ratio;

	if (current_state == active_state)
		ratio = RATIO_OFFSPRING_ACTIVE;

	else
		ratio = RATIO_OFFSPRING_STUCK;


	int max_selected = round(2 * population_size * ratio);

	while(max_selected)
	{
		if (max_selected % 4 != 0)
			max_selected -= 1;

		else
			break;
	}

	if (max_selected < 4)
		max_selected = 4;


	int group_choice;
	int member_choice;

	int first_margin = 70, second_margin = 90;

	if (current_state == stuck_state)
		second_margin = 95;


	//std::random_device rd;
	unsigned seed = 1;
	std::default_random_engine generator (seed);//(rd());
	std::uniform_int_distribution<int> main_distribution(1, 100);

	// the order in which members take part in the tournament
	vector<int> order_ind;

	while (order_ind.size() < max_selected)
	{
		// choose the group
		group_choice = main_distribution(generator);

		// first group with 0.7 probability
		if (group_choice < first_margin && first_class_ind.size() != 0)
		{
			member_choice = first_class_ind[rand() % first_class_ind.size()];
			order_ind.push_back(member_choice);
		}

		// second group with 0.2 probability
		else if (group_choice >= first_margin && group_choice < second_margin && second_class_ind.size() != 0)
		{
			member_choice = second_class_ind[rand() % second_class_ind.size()];
			order_ind.push_back(member_choice);
		}

		// third group with 0.1 probability 
		else if(group_choice >= second_margin && third_class_ind.size() != 0)
		{
			member_choice = third_class_ind[rand() % third_class_ind.size()];
			order_ind.push_back(member_choice);
		}
	}

	return order_ind;
}


vector<int> GeneticAlgorithm_OA :: tournament_selection(vector<float>& feasibility, vector<int>& order_ind, vector<vector<float>>& fitness_values)
{
	// randomly select 2 members
	// - an infeasible solution loses to a feasible one;
	// - if both individuals are feasible, the one from the further front loses;
	// if both are from the same front, the more crowded one loses
	// - if both individuals are infeasible, the one with greatest constraint violation loses

	// members, chosen after the tournament
	vector<int> selected_ind;

	// for each 2 members
	for (int i = 0; i < order_ind.size() - 1; i += 2)
	{
		int a = order_ind[i];
		int b = order_ind[i + 1];

		// both are feasible - select the one in the first fronts and lowest crowding distance
		if ( (current_mode == RSA_multi || current_mode == OA_placement_multi || current_mode == Tree_Establishment_multi) &&
			feasibility[a] == 1 && feasibility[b] == 1)
		{
            // compare the crowding distances
            if (front_number[a] == front_number[b])
			{
				if (crowding_distances[a] == crowding_distances[b])
					selected_ind.push_back(fitness_values[0][a] < fitness_values[0][b] ? a : b);

				else
                   	selected_ind.push_back(crowding_distances[a] > crowding_distances[b] ? a : b);
			}

            else
                selected_ind.push_back(front_number[a] < front_number[b] ? a : b);
		}

		else if ( (current_mode == Ordering || current_mode == RSA_single || current_mode == OA_placement_single || current_mode == Tree_Establishment_single) &&
			feasibility[a] == 1 && feasibility[b] == 1)
			selected_ind.push_back(fitness_values[0][a] < fitness_values[0][b] ? a : b);

		// select the feasible one
		else if (feasibility[a] == 1 && feasibility[b] != 1)
			selected_ind.push_back(a);

		else if (feasibility[a] != 1 && feasibility[b] == 1)
			selected_ind.push_back(b);

		// select the one closest to feasibility
		else
			selected_ind.push_back(feasibility[a] > feasibility[b] ? a : b);
	}

	return selected_ind;
}


int GeneticAlgorithm_OA :: crossover(vector<int>& selected_ind)
{
	// take two members from the chosen list
	// split each one in half
	// create two new ones

	// probability to have a crossover
	float margin = CROSSOVER_PROB_ACTIVE * selected_ind.size();

	if (current_state == stuck_state && hetacomb_counter < max_hetacomb_counter)
		margin = CROSSOVER_PROB_STUCK_1 * selected_ind.size();

	else if (current_state == stuck_state && hetacomb_counter == max_hetacomb_counter)
		margin = CROSSOVER_PROB_STUCK_2 * selected_ind.size();

	// for the consecutive pairs of the selected members 
	for (int count = 0; count < selected_ind.size() - 1; count += 2)
	{
		if(current_mode != Ordering)
		{
			int temp = rand() % selected_ind.size();

			// with some probability there is no crossover
			if (temp < margin)
			{
				// choose the point at which to switch the parts
				int cross_position = rand() % gene_length;

				crossover_op(population[selected_ind[count]], population[selected_ind[count+1]], cross_position);
			}
		}

		new_population[count] = population[selected_ind[count]];
		new_population[count + 1] = population[selected_ind[count + 1]];
	}

	return 0;
}


int GeneticAlgorithm_OA :: recreate_population(int num_new_solutions)
{
	// if we've reached the new cost and lost that solution immediately
    // or there are too few best solutions
	if ( current_state == active_state && ( (feasible_found == false && best_solutions_feasible.size() != 0) ||
		 (generation_num - gen_best_cost < 5 && current_best_cost < best_cost) || best_solutions_feasible.size() < 3) )
	{
		int i = 0;

		for(auto s_iter = best_solutions_feasible.begin(); s_iter != best_solutions_feasible.end(); s_iter ++)
		{
			if(i > 50 || num_new_solutions >= population_size)
				break;

			new_population[num_new_solutions ++] = (*s_iter);

			i ++;
		}

		if(fast_run == false && VERBOSE_DEBUG)
			LogFile << endl << "Elitism performed with : " << i << "solutions added" << endl;
	}


    bool permutable = false;

    if(current_mode == Tree_Establishment_single || current_mode == Tree_Establishment_multi)
        permutable = true;

	
	// set the default ordering: 0, 1, 2, ... for every solution
	vector<int> ordering_default;
	for(int i = 0; i < chromosome_struct.size(); i ++)
		ordering_default.push_back(i);
		

	// generate the remaining members to keep the population size the same
	for (int i = num_new_solutions; i < population_size; i ++)
	{
		if(current_mode == Ordering)
		{
			random_shuffle(ordering_default.begin(), ordering_default.end());
			new_population[i] = GA_Solution_OA(chromosome_struct, ordering_default, permutable);
		}
		
		else
			new_population[i] = GA_Solution_OA(chromosome_struct, permutable);
	}
    

	// move the new solutions to the population
	for (int i = 0; i < population.size(); i ++)
		population[i] = move(new_population[i]);
	
	return 0;
}


int GeneticAlgorithm_OA :: mutation(int num_new_solutions)
{
	int max_number = mutation_prob_vect.size() * mutation_prob_vect.size();

	// for each population member
	for (int i = 0; i < num_new_solutions; i ++)
	{
		// generate a number from a matrix
		int temp = rand() % max_number;

		int flip_genes = 0;

		// find in which row this number is
		for(int j = 0; j < mutation_prob_vect.size(); j ++)
		{
			if (binary_search(mutation_prob_vect[j].begin(), mutation_prob_vect[j].end(), temp) == true)
			{
				flip_genes = j;
				break;
			}
		}

		if(current_mode == Mode::Ordering)
			flip_genes *= 4;

		// for a number of genes
		for (int j = 0; j < flip_genes; j ++)
		{
			// generate a random position in a gene
			int position = rand() % gene_length;

			// exchange 2 genes of the same solution
			if(current_mode == Mode::Ordering)
			{
				// generate a random position in a gene
				int position_two = position;
				
				while(position_two == position)
				{
					position_two = rand() % gene_length;
				}

				new_population[i].swap_genes(position, position_two);
			}		

			// mutate the gene
			else
				new_population[i].mutation_op(position);
		}
	}

	return 0;
}


int GeneticAlgorithm_OA :: change_mutation_pattern()
{
	//if (current_mode == RSA_multi && current_state == stuck_state)
	//	return 0;

	int last_row_of_low_mutations = round(gene_length * FINAL_SMALL_MUTATIONS);

	if (last_row_of_low_mutations < 1)
		last_row_of_low_mutations = 2;


	if (current_state == active_state && row_of_mutation_matrix < last_row_of_low_mutations)
		return 0;

	if (current_state == stuck_state && row_of_mutation_matrix == mutation_prob_vect.size() - 1)
		return 0;


	int num_elements_2_move = round(gene_length * RATE_OF_LOWERING_MUTATION_RATE);

	if (num_elements_2_move < 1)
		num_elements_2_move = 1;

	if (current_state == stuck_state)
		num_elements_2_move *= 2;


	int num_of_residual_large_mutations = round(gene_length * RESIDUAL_LARGE_MUTATIONS);

	if (num_of_residual_large_mutations < 1)
		num_of_residual_large_mutations = 1;


	int row_to_push_ind;

	for (int i = 0; i < num_elements_2_move; i ++)
	{
		// choose the row where to push
		if (current_state == stuck_state)
		{
			row_to_push_ind = (generation_num + i) % mutation_prob_vect.size();

			if (row_to_push_ind <= row_of_mutation_matrix)
				continue;
		}

		else if (current_state == active_state)
		{
			row_to_push_ind = (generation_num - 1 + i) % row_of_mutation_matrix;

			if (row_to_push_ind == 0)
				continue;
		}


		int temp;

		// if possible, push
		if ( (current_state == active_state && mutation_prob_vect[row_of_mutation_matrix].size() > num_of_residual_large_mutations) ||
			(current_state == stuck_state && mutation_prob_vect[row_of_mutation_matrix].size() > mutation_prob_vect.size()) )
		{
			temp = mutation_prob_vect[row_of_mutation_matrix].back();
			mutation_prob_vect[row_of_mutation_matrix].pop_back();
			mutation_prob_vect[row_to_push_ind].push_back(temp);
		}

		// if not, go to the next row
		else
		{
			if (current_state == stuck_state)
				row_of_mutation_matrix ++;

			else if (current_state == active_state)
				row_of_mutation_matrix --;

			break;
		}
	}

	for(int i = 0; i < mutation_prob_vect.size(); i ++)
		sort(mutation_prob_vect[i].begin(), mutation_prob_vect[i].end());

	if (fast_run == false && VERBOSE_DEBUG)
	{
		LogFile << endl;

		for(int i = 0; i < mutation_prob_vect.size(); i ++)
		{
			for (int j = 0; j < mutation_prob_vect[i].size(); j ++)
				LogFile << mutation_prob_vect[i][j] << " ";

			LogFile << endl;
		}
		LogFile << endl;
	}

	return 0;
}


vector<GA_Solution_OA> GeneticAlgorithm_OA :: get_best_solutions()
{
	if(best_solutions_feasible.size() != 0)
		return vector<GA_Solution_OA>(best_solutions_feasible.begin(), best_solutions_feasible.end());

	else
		return vector<GA_Solution_OA>(best_solutions_unfeasible.begin(), best_solutions_unfeasible.end());
}


int GeneticAlgorithm_OA :: set_best_solutions()
{
	if(best_solutions_feasible.size() != 0)
	{
		population_size = best_solutions_feasible.size();
		population.clear();

		for(auto it = best_solutions_feasible.begin(); it != best_solutions_feasible.end(); it ++)
			population.push_back(*it);
	}

	else
	{
		population_size = best_solutions_unfeasible.size();
		population.clear();

		for(auto it = best_solutions_unfeasible.begin(); it != best_solutions_unfeasible.end(); it ++)
			population.push_back(*it);
	}

	//new_population = population;

	return population_size;
}