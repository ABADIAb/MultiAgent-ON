#ifndef GeneticAlgorithm_OA_H
#define GeneticAlgorithm_OA_H

#define EPS 1e-6

#define INIT_FIT_VALUE 1e+6


// initial num_flipped_genes = gene_length * RATIO_OF_GENES_MUTATED_INIT
#define RATIO_OF_GENES_MUTATED_INIT 0.03

// defines the number of mutations that are higly probable by the end of the active state
#define FINAL_SMALL_MUTATIONS 0.01

// defines the probability of having high number of mutations by the end of the active state
#define RESIDUAL_LARGE_MUTATIONS 0.01

// defines the rate with which the probability of having high number of mutation 
// decreases in the active state and increases in the stuck state
#define RATE_OF_LOWERING_MUTATION_RATE 0.01


// best_fit_margin = best_fit_value * RATIO_BEST_FIT_MARGIN
// defines how the chromosomes are selected for the tournament
#define RATIO_BEST_FIT_MARGIN_MIN 0.005
#define RATIO_BEST_FIT_MARGIN_MAX 0.05

// defines the proximity to the suboptimum for the hetacomb to happen
#define RATIO_CLOSE_TO_OPTIMUM 0.05

// if after this number of generations there is no improvement in fitness 
// and there are suboptimal solutions in the population, hetacomb happens
#define GEN_BEFORE_BEING_STUCK 25


// this part of the population participates in the tournament if a feasible solution has been found or not
#define RATIO_OFFSPRING_ACTIVE 0.95
#define RATIO_OFFSPRING_STUCK 0.95

// probability of the crossover in the active and stuck states
#define CROSSOVER_PROB_ACTIVE 0.5
#define CROSSOVER_PROB_STUCK_1 0.3
#define CROSSOVER_PROB_STUCK_2 0.3

// the desired maximum number of fronts
#define MAX_FRONT_NUM 25


// whether inputs in INIT_FILE_NAME are in binary (1/0 - placed/not) or indexes of active location
#define BINARY_INIT_INPUT 0

#define INIT_FILE_NAME_OA "OA_GA_init.txt"
#define INIT_FILE_NAME_TE "TE_GA_init.txt"
#define LOG_FILE_NAME "OA_GA_log.txt"
#define FRONT_EVO_FILE "OA_GA_opt_front.txt"


#include "GA_Solution_OA.h"

#include <vector>
#include <unordered_set>
#include <string>
#include <map>
#include <fstream>
#include <iostream>
using namespace std;

namespace NS_NBGA
{
	class GeneticAlgorithm_OA
	{
	// Interfaces
		public:

			// which problem is being solved
			enum Mode {Ordering, RSA_single, RSA_multi, OA_placement_single, OA_placement_multi, Tree_Establishment_single, Tree_Establishment_multi};

			GeneticAlgorithm_OA(int pop_size, vector<vector<float>>& chromosome_struct, Mode mode, bool active_clusters = false, bool short_run = false);
			~GeneticAlgorithm_OA();

			int create_solution(vector<bool> genes, bool permutable, int ind) 
			{
				if(ind >= population.size())
					throw runtime_error("Invalid index");
					
				population[ind] = GA_Solution_OA(chromosome_struct, genes, permutable);
				return 0;
			}

			int create_solution(vector<int> genes, bool permutable, int ind) 
			{
				if(ind >= population.size())
					throw runtime_error("Invalid index");

				population[ind] = GA_Solution_OA(chromosome_struct, genes, permutable);
				return 0;
			}

			int change_solution(int index, vector<int> genes, bool permutable)
			{
				population[index] = GA_Solution_OA(chromosome_struct, genes, permutable);
				return 0;
			}

			float get_selected_gene(int solution_ind, int gene_ind)
			{
				return population[solution_ind].get_active_ind(gene_ind);
			}

			float get_selected_gene_unique(int solution_ind, int gene_ind)
			{
				if(solution_ind >= unique_solutions.size())
					throw runtime_error("Invalid index");

				return unique_solutions[solution_ind].get_active_ind(gene_ind);
			}

			int is_selected_gene_active(int solution_ind, int gene_ind)
			{
				if(solution_ind >= population.size())
					throw runtime_error("Invalid index");

				return population[solution_ind].is_active(gene_ind);
			}

			int is_selected_gene_unique_active(int solution_ind, int gene_ind)
			{
				if(solution_ind >= unique_solutions.size())
					throw runtime_error("Invalid index");

				return unique_solutions[solution_ind].is_active(gene_ind);
			}

			int print_solution(int solution_ind, ofstream& file, int option)
			{
				population[solution_ind].print(file, option);
				return 0;
			}

			int print_unique_solution(int solution_ind, ofstream& file, int option)
			{
				unique_solutions[solution_ind].print(file, option);
				return 0;
			}

			pair<bool, float> find_feasible_solution(int solution_ind);

			int first_generation();
			int next_generation(vector<float>& feasibility, vector<vector<float>>& fitness_values);

			bool is_improved() const { return current_state != finish_state; }
			bool is_feasible() const { return feasible_found; }
			bool is_stuck() const { return current_state == stuck_state; }
			int get_generation_number() const { return generation_num; }
			float get_best_cost() const { return best_cost; }

			int find_unique_solutions(vector<int>& matching_list);
			vector<GA_Solution_OA> get_best_solutions();
			int set_best_solutions();

	// ******************************************************************

        // possible states of the algorithm
	    enum State {active_state, stuck_state, finish_state};

	// General Variables

		// structure of the chromosome - each cluster contains the weight of one or multiple genes
		vector<GeneCluster_OA> chromosome_struct;

		// each solution - a sequence of 0/1
		vector<GA_Solution_OA> population;
		vector<GA_Solution_OA> new_population;

		vector<GA_Solution_OA> unique_solutions;

		Mode current_mode;

		bool fast_run;

		int population_size; // even number!!!
		
		int gene_length;	 // number of clusters

		int generation_num;

		bool feasible_found;

		State current_state;
		int gen_in_current_state;

		// generations before deleting the best members of the population
		int gen_before_hetacomb;

		// number of perfromed hetacombs while being in the stuck state
		int hetacomb_counter;

		// after reaching this number of unsuccesful hetacombs,
		// try reducing probability of crossvoer and increase mutations
		int max_hetacomb_counter;


	// Variables that describe Pareto fronts

		// number of the front to which the solution belongs
		vector<int> front_number;

		// maximal (less optimal) front in the population
		int max_front_num;

		// some descriptors of thte distribution of solutions among the fronts
		// used to choose solutions for the tournament
		int first_feasible_front_ind;
		int middle_feasible_front_ind;
		int last_opt_front_ind;		// last front containing the current optimal solution

		// crowding distances in the objective space for each member 
		// (smaller - the more dense the neighbourhood is)
		// for details see fitness_calculation function or NSGA-II algorithm
		vector<float> crowding_distances;


	// Variables that describe the process of mutation

		// matrix that defines the distribution of the number of mutations
		vector<vector<int>> mutation_prob_vect;

		// the upper bound of the number of mutations with a realistic probability
		int row_of_mutation_matrix;


	// Variables that describe the process of looking for the optimum

		// best solution and the generation it was found
		float best_cost;
		int gen_best_cost;

		// solutions with fitness <= best_fitness_ever_found * BEST_FITNESS_MARGIN
		// are eliminated during the hetacomb if the algorithm gets stuck in the local minimum
		float best_cost_margin;

		// if solution isn't feasible, closest to feasibility are saved
		float best_feasibility_val;
		int gen_best_feasibility_val;
		float best_feasibility_margin;

		float current_best_cost;
		float current_best_feasibility;


		// all the best solutions found
		unordered_set<GA_Solution_OA, GA_Solution_OA::HashFunction> best_solutions_feasible;
        unordered_set<GA_Solution_OA, GA_Solution_OA::HashFunction> best_solutions_unfeasible;

		unordered_set<GA_Solution_OA, GA_Solution_OA::HashFunction> feasible_solutions;


	// Variables for logging purposes
		ofstream LogFile;
		ofstream ObjFile;

	// ******************************************************************

	// Functions

		// preprocess fitness values for different modes
		int fitness_calculation(vector<float>& feasibiity, vector<vector<float>>& fitness_values);
        
        int hetacomb(map<float, int>& cost_distribution, map<float, int>& feasibility_distribution, vector<float>& feasibility, vector<vector<float>>& fitness_values);
		int ranking(vector<float>& feasibility, vector<vector<float>>& fitness_values);
		int crowding_distance_computation(vector<int>& front_ind, vector<vector<float>>& fitness_values);

		bool dominates(vector<float>& one, vector<float>& two);

		vector<int> preselection(vector<float>& feasibility, vector<vector<float>>& fitness_values);

		vector<int> tournament_selection(vector<float>& feasibility, vector<int>& order_ind, vector<vector<float>>& fitness_values);
		
		int crossover(vector<int>& selected_ind);
				
		int mutation(int num_new_solutions);

		int recreate_population(int num_new_solutions);	
		
		int change_mutation_pattern();

		int switch_state(State new_state);

		int process_feasible_solutions(vector<float>& feasibility, vector<vector<float>>& fitness_values);

	// ******************************************************************
	};
};

#endif