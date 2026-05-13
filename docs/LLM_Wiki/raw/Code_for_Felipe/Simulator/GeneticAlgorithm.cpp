#include "GeneticAlgorithm.h"

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

#define VERBOSE_DEBUG 0

GeneticAlgorithm :: GeneticAlgorithm (int pop_size, vector<vector<float>>& ch_struct, vector<vector<int> > mutation_parts, 
						vector<vector<int> > important_mutation_parts, Mode mode, bool all_clusters_active, bool short_run, bool show_status, int max_number_gen)
{
	// check that the population size is even
	if (pop_size % 2 != 0)
	{
		cout << "Population size is " << pop_size << endl;
		throw invalid_argument("Population_size must be even");
	}

 	// current date/time based on current system
 	time_t now = time(0);

	// initiate the log file
	if(short_run == false)
	{
		LogFile = ofstream(LOG_FILE_NAME, ios::out | ios::trunc);

		if (!LogFile.is_open())
			throw ifstream::failure("Failed to open the log file" + string(LOG_FILE_NAME));

		LogFile << endl << endl << "***************************" << endl;
		LogFile << ctime(&now) << "***************************" << endl;
	}
	
	population_size = pop_size; // set the population size

	gene_length = ch_struct.size(); // set the number of gene clusters

	// at least one of the genes in the gene cluster has to be active if true
	bool always_active = all_clusters_active;

	// form the chromosome from the weights
	for (int i = 0; i < ch_struct.size(); i ++)
	{
		// for each gene cluster, add an instance of GeneCluster to the chromosome structure
		// arguments are (the size of gene cluster which is the number of genes inside it, always_avtice)
		chromosome_struct.push_back(GeneCluster(ch_struct[i].size(), mutation_parts[i], important_mutation_parts[i], always_active));
	}

	current_mode = mode; // set the mode

	// if it is true, slip some parts in order to be faster (don't log, stop faster, ...)
	fast_run = short_run; // set the fast run

	// if it is true, will show the status on the terminal
	print_status = show_status; // set the print status

	// set the maximum number of generations, it stopes at this number
	// if it is equal to 0, other conditions will be applied for stopping
	max_number_generation = max_number_gen; 

	generation_num = 1; // init the generation number

	switch_state(active_state); // set state as acvtive

	feasible_found = false; // init the feasible found status

	gen_before_hetacomb = 0; // init the generation before hetacomb happen

	// margin of the hetacomb gets increased by 0.05 every 2 hetacombs
	max_hetacomb_counter = (RATIO_BEST_FIT_MARGIN_MAX - RATIO_BEST_FIT_MARGIN_MIN) / 0.005 * 2;

	// set initial best fitness value to the maximum
	best_cost = INIT_FIT_VALUE;

	// init the generation at which the best fitness value was reached
	gen_best_cost = 1;

	// init the margin of best cost
	best_cost_margin = RATIO_BEST_FIT_MARGIN_MIN * best_cost;

	// set initial current best fitness value to the maximum
	current_best_cost = INIT_FIT_VALUE;

	// set initial best feasibility value to the minimum
	best_feasibility_val = 0;

	// init the generation at which the best feasibility value was reached
	gen_best_feasibility_val = 1;

	// init the margin of best feasibility
	best_feasibility_margin = 0;

	// set initial current best feasibility value to the minimum
	current_best_feasibility = 0;

	// initialize the mutation pattern, at least 3 rows are needed for the matrix
	row_of_mutation_matrix = round(gene_length * RATIO_OF_GENES_MUTATED_INIT);
	if (row_of_mutation_matrix < 3)
		row_of_mutation_matrix = 3;

	// log the rows of mutatiopn matrix
	if (short_run == false && VERBOSE_DEBUG)
	{
		LogFile << endl << row_of_mutation_matrix << " genes are flipped out of " << gene_length << endl;
	}

	// fill row_of_mutation_matrix vectors with numbers from 0 to row_of_mutation_matrix * row_of_mutation_matrix
	vector<int> temp;
	int counter = 0;
	for (int i = 0; i < row_of_mutation_matrix; i ++)
	{
		temp.clear();
		for (int j = 0; j < row_of_mutation_matrix; j ++)
		{
			temp.push_back(counter++);
		}
		mutation_prob_vect.push_back(temp);
	}

	// row indexes are counted from 0, so subtract 1
	row_of_mutation_matrix --;

	// log the initial mutation matrix
	if (short_run == false && VERBOSE_DEBUG)
	{
		for(int i = 0; i < mutation_prob_vect.size(); i ++)
		{
			for (int j = 0; j < mutation_prob_vect[i].size(); j ++)
			{
				LogFile << mutation_prob_vect[i][j] << " ";
			}

			LogFile << endl;
		}
		LogFile << endl;
	}
}


GeneticAlgorithm :: ~GeneticAlgorithm()
{
	// when finished, log the time and close the log file
	if(fast_run == false)
	{
		time_t now = time(0);

		LogFile << endl << endl << "**********THE END***********" << endl;
		LogFile << ctime(&now) << "***************************" << endl;

		LogFile.close();
	}
}


int GeneticAlgorithm :: first_generation(bool init, vector<vector<int> > GA_initializer_vector)
{   
    // pass this to the GA_Solution to compare different tree establishments properly
    bool permutable = false;

	// randomly generate the first generation
	for (int i = 0; i < population_size; i ++)
	{
		population.push_back(GA_Solution(chromosome_struct, permutable));
	}

	new_population = population;

	// if init variable is set, initialize the first population with the given vector 
	if(current_mode == NB_placement && init)
	{
		for (int i = 0; i < GA_initializer_vector.size(); i++)
		{
			population[i] = GA_Solution(chromosome_struct, GA_initializer_vector[i], permutable);
		}
	}

	return 0;
}


int GeneticAlgorithm :: find_unique_solutions(vector<int>& matching_list)
{
	unique_solutions.clear();

	unordered_set<GA_Solution, GA_Solution::HashFunction> s;

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
			vector<GA_Solution>::iterator it = find(unique_solutions.begin(), unique_solutions.end(), population[i]);
        	int ind = it - unique_solutions.begin();

			matching_list.push_back(ind);
		}
	}

	return unique_solutions.size();
}


int GeneticAlgorithm :: next_generation(vector<float>& feasibility, vector<vector<float>>& fitness_values)
{
	// auto t1 = std::chrono::high_resolution_clock::now();

	// find the best solutions in this generation and perform hetacomb if needed
	fitness_calculation(feasibility, fitness_values);

	/*
	auto t2 = std::chrono::high_resolution_clock::now();
	auto duration = std::chrono::duration_cast<std::chrono::microseconds>( t2 - t1 ).count();
	if (fast_run == false && VERBOSE_DEBUG)
    	LogFile << "******** Fitness, mks: " << duration << " ********" << endl;
	*/

	// select members for the tournament
	vector<int> order_ind = preselection(feasibility, fitness_values);

	/*
	auto t3 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t3 - t2 ).count();
	if (fast_run == false && VERBOSE_DEBUG)
  		LogFile << "******** Preselection, mks: " << duration << " ********" << endl;
	*/

	// compare solutions by their fitness and feasibilities
	vector<int> selected_ind = tournament_selection(feasibility, order_ind, fitness_values);

	/*
	auto t4 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t4 - t3 ).count();
	if (fast_run == false && VERBOSE_DEBUG)
    	LogFile << "******** Tournament, mks: " << duration  << " ********" << endl;
	*/

	crossover(selected_ind);

	/*
	auto t5 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t5 - t4 ).count();
	if (fast_run == false && VERBOSE_DEBUG)
    	LogFile << "******** Crossover, mks: " << duration  << " ********" << endl;
	*/

	// mutation
	mutation(selected_ind.size());

	/*
	auto t6 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t6 - t5 ).count();
    if (fast_run == false && VERBOSE_DEBUG)
    	LogFile << "******** Mutation, mks: " << duration  << " ********" << endl;
	*/
	
	// fill the population to the original size
	recreate_population(selected_ind.size());

	/*
	auto t7 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t7 - t6 ).count();
    if (fast_run == false && VERBOSE_DEBUG)
    	LogFile << "******** Recreate, mks: " << duration  << " ********" << endl;
	*/

	// tweak the probability distribution of the number of mutations happening
	change_mutation_pattern();

	/*
	auto t8 = std::chrono::high_resolution_clock::now();
	duration = std::chrono::duration_cast<std::chrono::microseconds>( t8 - t7 ).count();
    if (fast_run == false && VERBOSE_DEBUG)
    	LogFile << "******** Change mutation, mks: " << duration  << " ********" << endl << endl;
	*/


	// stopping condition when fast run is active
	if(fast_run)
	{
		if (!feasible_found && generation_num > 50)
			switch_state(finish_state);

		else if ((feasible_found) && ((generation_num - gen_best_cost > 25) || (generation_num == 100)))
			switch_state(finish_state);
	}
	// stopping condition when fast run is not active 
	else
	{
		// finish
		if (max_number_generation == 0)
		{
			if (feasible_found && current_state == stuck_state)
			{
				if(gen_in_current_state > gene_length * 5)
					switch_state(finish_state);
			}
				
			else if (feasible_found == false && current_state == stuck_state)
			{
				if(gen_in_current_state > (int)gene_length * 5)
					switch_state(finish_state);
			}
		}

		else
		{
			if (feasible_found && generation_num > max_number_generation)
				switch_state(finish_state);
		}
	}

	generation_num ++;
	gen_in_current_state ++;

	return 0;
}


int GeneticAlgorithm :: switch_state(State new_state)
{
	current_state = new_state; // set the new state
	
	// reset the number of generations in current state
	gen_in_current_state = 0;

	// log the change
	if(fast_run == false)
		LogFile << endl << "**** State changed to ";
	

	switch (new_state)
	{
		case active_state:
			// log the new state
			if(fast_run == false)
				LogFile << "active state";
			
			// reset the row of mutation matrix, at least 3 rows needed
			row_of_mutation_matrix = round(gene_length * RATIO_OF_GENES_MUTATED_INIT);
			if (row_of_mutation_matrix < 3)
				row_of_mutation_matrix = 3;

			// row indexes are counted from 0, so subtract 1
			row_of_mutation_matrix --;

			hetacomb_counter = 0; // reset the hetacomb counter

			break;

		case stuck_state:
			// log the new state
			if(fast_run == false)
				LogFile << "stuck state";

			row_of_mutation_matrix = 1;

			hetacomb_counter = 0; // reset the hetacomb counter
			break;

		case finish_state:
			// log the new state
			if(fast_run == false)
				LogFile << " finish state";
			break;
	}

   	if(fast_run == false)
		LogFile << "****" << endl;

	return 0;
}


int GeneticAlgorithm :: fitness_calculation(vector<float>& feasibility, vector<vector<float>>& fitness_values)
{
	// check whether there are feasible solutions
	// (required if all feasible ones were deleted in the hecatomb at the previous generation)
	float max_feas = 0;
	for (int i = 0; i < population_size; i ++)
		if(feasibility[i] > max_feas)
			max_feas = feasibility[i];

	// if there is no feasible solution anymore and 
	// there was at least one feasible solution in the previous generations
	if (max_feas != 1.0 && feasible_found == true)
	{
		LogFile << "No feasible solutions present anymore" << endl;
		// any feasible solutions will be saved from now on, but only new ones (best_solutions_feasible isn't cleared)

		feasible_found = false; // reset the feasible fount status

		best_cost = INIT_FIT_VALUE; // reset the best fitness value to maximum

		best_feasibility_val = max_feas - 1e-3; // reset the best feasibility value

		 // reset the generation number in which the new best feaibility value is found
		gen_best_feasibility_val = generation_num;
	}

	
	// for debugging only
	map<float, int> cost_distribution;
	map<float, int> feasibility_distribution;

	current_best_cost = INIT_FIT_VALUE; // init the current best fitness value to the maximum
	current_best_feasibility = 0; // init the current best feasibility value to the minimum

	// check every solution in the population and look for the new best solutions
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
		// if it is feasible and its fitness is close to the best fitness and if it is a new solution
		if (feasibility[i] == 1.0 && fitness_values[0][i] < (best_cost + fabs(best_cost) * RATIO_CLOSE_TO_OPTIMUM) && 
			find(best_solutions_feasible.begin(), best_solutions_feasible.end(), population[i]) == best_solutions_feasible.end() )
		{
			// primary fitness minimization is the main goal
			// if a new solution is smaller or equal
			if (fitness_values[0][i] <= best_cost + EPS)
			{
				// strictly smaller than the current best
				if (fitness_values[0][i] < best_cost - EPS)
				{
					// log the new best solution
					if(fast_run == false)
					{
						LogFile << endl << "New best solution found at generation " << generation_num << " with a obj " << fitness_values[0][i] << endl;	
						population[i].print(LogFile, 2);
						LogFile << endl;
					}

					// if there was no feasible solution before this
					if (feasible_found == false)
					{
						// set the feasible found status as true and the best feasibility value as 1
						// because a new feasible solution has been found
						feasible_found = true;
						best_feasibility_val = 1.0;

						best_solutions_unfeasible.clear(); // unfeasible results are cleared

						// set the current best fitness value equal to the fitness of the new best solution
						current_best_cost = fitness_values[0][i];

						cost_distribution[(int)round(fitness_values[0][i])] ++; // add to the cost distribution
					}

					// switch the state to active if currently in stuck
					if (current_state == stuck_state)
						switch_state(active_state);

					best_cost = fitness_values[0][i]; // update the best fitness value

					// update the generation in which the new best fitness was found
					gen_best_cost = generation_num;

					// tweak the margin
					best_cost_margin = RATIO_BEST_FIT_MARGIN_MIN * fabs(best_cost);
				
					//best_solutions_feasible.clear();
				}
					
				// save the new best solution
				best_solutions_feasible.insert(population[i]);
			}
		}

		// if it is not feasible and its feasibility is greater than the best one, and if it is a new solution
		else if (feasible_found == false && feasibility[i] != 0 && feasibility[i] > (best_feasibility_val - EPS) && 
			find(best_solutions_unfeasible.begin(), best_solutions_unfeasible.end(), population[i]) == best_solutions_unfeasible.end())
		{
			// with a strictly better feasibility
			if (feasibility[i] > best_feasibility_val + EPS)
			{
				// log the new unfeasible solution
				if(fast_run == false)
				{
					LogFile << endl << "Solution closer to feasible found at generation " << generation_num << " with feasibility " << feasibility[i] << endl;
					population[i].print(LogFile, 2);
					LogFile << endl;
				}

				best_feasibility_val = feasibility[i]; // update the best feasibility value

				// update the generation in which the new best feasibility was found
				gen_best_feasibility_val = generation_num;

				// tweak the margin
				if (current_mode == NB_placement)
				{
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


	// switch the state to stuck if no improvement
	// condition 1: - feasible solution has been found
	//              - currently in active state
	//              - some number of generations (GEN_BEFORE_BEING_STUCK) has been passed
	//				  and no better solution (in term of fitness value) found 
	// condition 2: - feasible solution has not been found yet
	//              - currently in active state
	//              - some number of generations (GEN_BEFORE_BEING_STUCK) has been passed
	//				  and no better solution (in term of feasibility value) found 
	if ( (feasible_found && current_state == active_state && (generation_num - gen_best_cost) > GEN_BEFORE_BEING_STUCK) ||
			(feasible_found == false && current_state == active_state && (generation_num - gen_best_feasibility_val) > GEN_BEFORE_BEING_STUCK) )
		switch_state(stuck_state);


    // delete the best solutions in the current generation if needed
    hetacomb(cost_distribution, feasibility_distribution, feasibility, fitness_values);

	// log the distribution of costs for fesible solutions in the population
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

	if(print_status) // print the status on terminal if true
	{
		cout << "Best fitness value at gen " << generation_num << " since gen " << gen_best_cost << "   is   " << best_cost << ", state: " << current_state << "    \t\t\t\r" << std::flush;
		//cin.ignore();
	}

	return 0;
}


int GeneticAlgorithm :: hetacomb(map<float, int>& cost_distribution, map<float, int>& feasibility_distribution, vector<float>& feasibility, vector<vector<float>>& fitness_values)
{
    if (current_state == stuck_state && gen_before_hetacomb != 0)
		gen_before_hetacomb --;

    // delay or force the hetacomb 
	if (feasible_found && current_state == stuck_state)
	{
		// find the cost with the most solutions in the population
		auto map_it = std::max_element(cost_distribution.begin(), cost_distribution.end(),[] 
		(const pair<int,int>& a, const pair<int,int>& b)
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
			gen_before_hetacomb += 4;

		// or if there is no variety of solutions 
		if (gen_before_hetacomb == 0 && cost_distribution.size() < 2)
			gen_before_hetacomb += 8;

		// log the generation before hetacomb
		if (fast_run == false && VERBOSE_DEBUG)
			LogFile << endl << gen_before_hetacomb << " before the next hetacomb" << endl;
	}

	else if (feasible_found == false && current_state == stuck_state)
	{
		// find the feasibility with the most solutions in the population
		auto map_it = std::max_element(feasibility_distribution.begin(), feasibility_distribution.end(),[] 
		(const pair<int,int>& a, const pair<int,int>& b)
		{ 
			return a.second < b.second;
		} );

		// force the hetacomb if there are too many (> 20) solutions with current max feasibolity
		// and we are halfway to the hetacomb because
		// most of them aren't unique but they fill the population
    	if (distance(feasibility_distribution.begin(), map_it) < 2 && map_it -> second > 20)
			gen_before_hetacomb = 0;

		// or if there is no variety of solutions 
		if (gen_before_hetacomb == 0 && feasibility_distribution.size() < 2)
			gen_before_hetacomb += 5;

		// log the generation before hetacomb
		if (fast_run == false && VERBOSE_DEBUG)
			LogFile << endl << gen_before_hetacomb << " before the next hetacomb" << endl;
	}
	
    // need to pass this to the GA_Solution to compare different tree etablishments properly
    bool permutable = false;
	
	// delete the best solutions of the population and fill them with random ones
	if (current_state == stuck_state && gen_before_hetacomb == 0)
	{
		// if we are close enough to the local optimum, get rid of the current best solutions
		if (feasible_found && current_best_cost < best_cost + 1)
		{
			best_cost_margin = 1; //0.05 * (hetacomb_counter / 2.0) + best_cost;
			//if ((generation_num - gen_best_cost) > GEN_BEFORE_BEING_STUCK * 10 && hetacomb_counter > 5)
			//	best_cost_margin = 0.01 * (hetacomb_counter / 2.0) * best_cost;

			// replace the solutions with fitness value lower than lower than best_cost + best_cost_margin
			int count = 0;
			for(int i = 0; i < population_size; i ++)
			{
				if(fitness_values[0][i] - best_cost < best_cost_margin)
				{
					population[i] = GA_Solution(chromosome_struct, permutable);

					count ++;
				}
			}

			// reset the number of generations before the next hetacomb
			gen_before_hetacomb = GEN_BEFORE_BEING_STUCK + 2 * hetacomb_counter;

			// increment the hetacomb counter if not reached to the maximum
			if (hetacomb_counter < max_hetacomb_counter)
				hetacomb_counter ++;

			// log the hetacomb information
			if (fast_run == false && VERBOSE_DEBUG)
			{
				LogFile << count << " solutions lower than " << best_cost + best_cost_margin << " deleted" << endl;
				LogFile << gen_before_hetacomb << " generations before the next hetacomb" << endl;

				if (hetacomb_counter == max_hetacomb_counter)
					LogFile << endl << "No more increase in hecatomb margin after " << best_cost_margin << endl;
			}

			// update the best fitness margin
			best_cost_margin = fabs(best_cost) * RATIO_BEST_FIT_MARGIN_MIN;
		}

		// only for OA placement, as finding a feasible solution in TE and RSA is very hard
		else if (!feasible_found && current_best_feasibility == best_feasibility_val)
		{
			best_feasibility_margin = 0.01; //0.01 + 0.025 * (hetacomb_counter / 2);

			// replace the solutions with feasibility value higher than lower than best_feasibility_val - best_feasibility_margin
			int count = 0;
			for(int i = 0; i < population_size; i ++)
			{
				if(best_feasibility_val - feasibility[i] < best_feasibility_margin)
				{
					population[i] = GA_Solution(chromosome_struct, permutable);

					count ++;
				}
			}

			// reset the number of generations before the next hetacomb
			gen_before_hetacomb = GEN_BEFORE_BEING_STUCK;

			// increment the hetacomb counter if not reached to the maximum
			if (hetacomb_counter < max_hetacomb_counter)
				hetacomb_counter ++;

			// log the hetacomb information
			if (fast_run == false && VERBOSE_DEBUG)
			{
				LogFile << count << " solutions with feasibility higher than " << best_feasibility_val - best_feasibility_margin << " deleted" << endl;
				LogFile << gen_before_hetacomb << " generations before the next hetacomb" << endl;

				if (hetacomb_counter == max_hetacomb_counter)
					LogFile << endl << "No more increase in hecatomb margin" << endl;
			}

			// update the best feasibility margin
			best_feasibility_margin = 0.02;
		}

		else
		{
			if (fast_run == false && VERBOSE_DEBUG)
				LogFile << "Too far from the local optimum to perform elimination: " << current_best_cost << endl;
		}
	}

    return 0;
}

bool GeneticAlgorithm :: dominates(vector<float>& one, vector<float>& two)
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


vector<int> GeneticAlgorithm :: preselection(vector<float>& feasibility, vector<vector<float>>& fitness_values)
{
	// create 3 groups: 
	// feasible, first fronts
	// feasible, middle fronts
	// infeasible, cost around the current best
	vector<int> first_class_ind;
	vector<int> second_class_ind;
	vector<int> third_class_ind;

	unordered_set<GA_Solution, GA_Solution::HashFunction> first_class;
	unordered_set<GA_Solution, GA_Solution::HashFunction> second_class;

	if (feasible_found)
	{
		// distribute the solutions into groups
		for (int i = 0; i < population_size; i ++)
		{
			// first group
			// feasible unique solutions close to best fitness with margin of RATIO_BEST_FIT_MARGIN_MIN
			if (feasibility[i] == 1.0 && 
				fitness_values[0][i] < current_best_cost + fabs(current_best_cost) * RATIO_BEST_FIT_MARGIN_MIN &&
				find(first_class.begin(), first_class.end(), population[i]) == first_class.end())
			{
				first_class_ind.push_back(i);
				first_class.insert(population[i]);
			}

			// second group
			// feasible unique solutions close to best fitness with margin of RATIO_BEST_FIT_MARGIN_MAX
			else if (feasibility[i] == 1.0 && 
				fitness_values[0][i] < current_best_cost + fabs(current_best_cost) * RATIO_BEST_FIT_MARGIN_MAX &&
				find(second_class.begin(), second_class.end(), population[i]) == second_class.end())
			{
				second_class_ind.push_back(i);
				second_class.insert(population[i]);
			}

			// third group
			// at most 50 unfeasible solutions with feasibility higher than 0.95
			else if (feasibility[i] >= 0.95 )//&& third_class_ind.size() < 200)
			{
				third_class_ind.push_back(i);
			}
		}
	}

	// no feasible solution found yet
	else if (feasible_found == false)
	{
		// distribute the solutions into groups
		for (int i = 0; i < population_size; i ++)
		{
			// slightly worse than the current best feasibility
			if (first_class_ind.size() < 250 && feasibility[i] > current_best_feasibility - best_feasibility_margin && 
				find(first_class.begin(), first_class.end(), population[i]) == first_class.end())
			{
				first_class_ind.push_back(i);
				first_class.insert(population[i]);
			}

			else if (second_class_ind.size() < 500 && feasibility[i] > current_best_feasibility - 2 * best_feasibility_margin &&
				find(second_class.begin(), second_class.end(), population[i]) == second_class.end())
			{
				second_class_ind.push_back(i);
				second_class.insert(population[i]);
			}

			else if (feasibility[i] > 0.5 && third_class_ind.size() < 1000)
				third_class_ind.push_back(i);
		}
	}

	// log the information of groups
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
		second_margin = 98;

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


vector<int> GeneticAlgorithm :: tournament_selection(vector<float>& feasibility, vector<int>& order_ind, vector<vector<float>>& fitness_values)
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
		int a = order_ind[i]; // first member
		int b = order_ind[i + 1]; // second member

		// if both are feasible the one with better fitness wins
		if (feasibility[a] == 1 && feasibility[b] == 1)
			selected_ind.push_back(fitness_values[0][a] < fitness_values[0][b] ? a : b);

		// if just one of them is feasible, the feasible one wins
		else if (feasibility[a] == 1 && feasibility[b] != 1)
			selected_ind.push_back(a);

		else if (feasibility[a] != 1 && feasibility[b] == 1)
			selected_ind.push_back(b);

		// if both are unfeasible the one with better feasibility wins
		else
			selected_ind.push_back(feasibility[a] > feasibility[b] ? a : b);
	}

	if(fast_run == false && VERBOSE_DEBUG)
			LogFile << endl << selected_ind.size() << " solutions are selected after tournament. " << endl;

	return selected_ind;
}


int GeneticAlgorithm :: crossover(vector<int>& selected_ind)
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
		int temp = rand() % selected_ind.size();

		// with some probability there is no crossover
		if (temp < margin)
		{
			// choose the point at which to switch the parts
			int cross_position = rand() % gene_length;

			crossover_op(population[selected_ind[count]], population[selected_ind[count+1]], cross_position);
		}

		new_population[count] = population[selected_ind[count]];
		new_population[count + 1] = population[selected_ind[count + 1]];
	}

	return 0;
}


int GeneticAlgorithm :: recreate_population(int num_new_solutions)
{
	// if we've reached the new cost and lost that solution immediately
    // or there are too few best solutions
	if ((current_state == active_state && ( (feasible_found == false && best_solutions_feasible.size() != 0) ||
		 (generation_num - gen_best_cost < 5 && current_best_cost < best_cost) || best_solutions_feasible.size() < 3)))
	{
		int i = 0;

		for(auto s_iter = best_solutions_feasible.begin(); s_iter != best_solutions_feasible.end(); s_iter ++)
		{
			if(i > 50 || num_new_solutions >= population_size)
				break;

			new_population[num_new_solutions ++] = (*s_iter);

			i ++;
		}

		if(fast_run == false)
			LogFile << endl << "Elitism performed with : " << i << "solutions added" << endl;
	}

    bool permutable = false;


	// generate the remaining members to keep the population size the same
	for (int i = num_new_solutions; i < population_size; i ++)
		new_population[i] = GA_Solution(chromosome_struct, permutable);
    

	// move the new solutions to the population
	for (int i = 0; i < population.size(); i ++)
		population[i] = move(new_population[i]);
	
	return 0;
}


int GeneticAlgorithm :: mutation(int num_new_solutions)
{
	int max_number = mutation_prob_vect.size() * mutation_prob_vect.size();

	// LogFile << endl << "# number of mutation: " << endl;
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
		// LogFile << flip_genes << ";";
		
		// for a number of genes
		for (int j = 0; j < flip_genes; j ++)
		{
			// generate a random position in a gene
			int position = rand() % gene_length;

			new_population[i].mutation_op(position);
		}
	}

	return 0;
}


int GeneticAlgorithm :: change_mutation_pattern()
{
	int last_row_of_low_mutations = round(gene_length * FINAL_SMALL_MUTATIONS);

	if (last_row_of_low_mutations < 1)
		last_row_of_low_mutations = 2;


	if (current_state == active_state && row_of_mutation_matrix < last_row_of_low_mutations)
	{
		return 0;
	}

	if (current_state == stuck_state && row_of_mutation_matrix == mutation_prob_vect.size() - 1)
	{
		return 0;
	}


	int num_elements_2_move = round(gene_length * RATE_OF_LOWERING_MUTATION_RATE);

	if (num_elements_2_move < 1)
		num_elements_2_move = 1;

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
			(current_state == stuck_state && mutation_prob_vect[row_of_mutation_matrix].size() > 4) )
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
			{
				LogFile << mutation_prob_vect[i][j] << " ";
			}
			LogFile << endl;
		}
		LogFile << endl;
	}

	

	

	return 0;
}


vector<GA_Solution> GeneticAlgorithm :: get_best_solutions()
{
	if(best_solutions_feasible.size() != 0)
		return vector<GA_Solution>(best_solutions_feasible.begin(), best_solutions_feasible.end());

	else
		return vector<GA_Solution>(best_solutions_unfeasible.begin(), best_solutions_unfeasible.end());
}


int GeneticAlgorithm :: set_best_solutions()
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

	new_population = population;
	return population_size;
}