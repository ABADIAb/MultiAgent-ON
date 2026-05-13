#include "GA_Solution_OA.h"

#include <random>
#include <set>
#include <iostream>
#include <map>
#include <memory>

using namespace NS_NBGA;
using namespace std;

// construct a solution by generating it randomly
GA_Solution_OA :: GA_Solution_OA(vector<GeneCluster_OA>& ch, bool permut)
{
	for(int i = 0; i < ch.size(); i ++)
		chromosome.push_back(std::make_unique<GeneCluster_OA>(GeneCluster_OA(ch[i])));
	
    permutable = permut;

	vector<bool>temp(chromosome.size());

	generate(temp.begin(), temp.end(), [] { return rand() % 2; });

    // mutate the original chromosome randomly
	for (int i = 0; i < chromosome.size(); i ++)
		if (temp[i])
			chromosome[i] -> mutation();

	valid_hash = false;
}


// construct a solution by turning genes on and off as in genes vector
GA_Solution_OA :: GA_Solution_OA(vector<GeneCluster_OA>& ch, vector<bool> genes, bool permut)
{
	for(int i = 0; i < ch.size(); i ++)
		chromosome.push_back(make_unique<GeneCluster_OA>(GeneCluster_OA(ch[i])));

    permutable = permut;

	// set the genes accordingly
	// if the cluster is turned on, first gene is set
	for (int i = 0; i < chromosome.size(); i ++)
		chromosome[i] -> turn_on_off(genes[i], 0);

	valid_hash = false;
}


// construct a solution by turning the exact gene in the cluster as in genes vector
GA_Solution_OA :: GA_Solution_OA(vector<GeneCluster_OA>& ch, vector<int> genes, bool permut)
{
	for (int i = 0; i < ch.size(); i ++)
		chromosome.push_back(make_unique<GeneCluster_OA>(GeneCluster_OA(ch[i])));

    permutable = permut;

    if(genes.size() != chromosome.size())
        throw invalid_argument("Not all the genes are presented to construct a solution");

	// set the chosen gene in the gene cluster
	for(int i = 0; i < chromosome.size(); i ++)
	{
		if (genes[i] != -1)
			chromosome[i] -> turn_on_off(true, genes[i]);

		else if (genes[i] == -1)
			chromosome[i] -> turn_on_off(false);
	}

	valid_hash = false;
}


GA_Solution_OA :: GA_Solution_OA(const GA_Solution_OA& sol)
{
	for(int i = 0; i < sol.chromosome.size(); i ++)
		this -> chromosome.push_back(make_unique<GeneCluster_OA>(GeneCluster_OA(*sol.chromosome[i])));

	this -> permutable = sol.permutable;
    
	this -> valid_hash = sol.valid_hash;
	this -> hash_val = sol.hash_val;

	this -> cost = sol.cost;
}


GA_Solution_OA :: GA_Solution_OA(GA_Solution_OA&& sol)
{
	this -> chromosome = move(sol.chromosome);

	this -> permutable = sol.permutable;

	this -> valid_hash = sol.valid_hash;
	this -> hash_val = sol.hash_val;

	this -> cost = sol.cost;
}


GA_Solution_OA& GA_Solution_OA::operator=(const GA_Solution_OA& sol)
{
	this -> chromosome.clear();

	for (int i = 0; i < sol.chromosome.size(); i ++)
		this -> chromosome.push_back(make_unique<GeneCluster_OA>(GeneCluster_OA(*sol.chromosome[i])));

	this -> permutable = sol.permutable;
	this -> valid_hash = sol.valid_hash;
	this -> hash_val = sol.hash_val;

	this -> cost = sol.cost;

	return *this;
}

GA_Solution_OA& GA_Solution_OA::operator=(GA_Solution_OA&& sol)
{
	this -> chromosome = move(sol.chromosome);

	this -> permutable = sol.permutable;
	this -> valid_hash = sol.valid_hash;
	this -> hash_val = sol.hash_val;

	this -> cost = sol.cost;

	return *this;
}


int GA_Solution_OA :: print(ofstream& File, int print_weights) const
{
    for(int i = 0; i < chromosome.size(); i ++)
	{
        if (chromosome[i] -> is_active())
		{
            if (print_weights == 1)
                File << i << " (" << chromosome[i] -> get_ind_active_gene() << "); ";
			
			else if (print_weights == 2)
				File << chromosome[i] -> get_ind_active_gene() << "; ";

			else
				File << i << "; ";
		}

		else
			File << "-1; ";
	}

    return 0;
}


namespace NS_NBGA
{
	int crossover_op(GA_Solution_OA& one, GA_Solution_OA& two, int pos)
	{
		if(one.chromosome.size() != two.chromosome.size())
			throw invalid_argument("Solutions should be of the same length to perform crossover");

		// copy the end from the other member
		for (int i = pos; i < one.chromosome.size(); i ++)
			cross_cluster_op(*one.chromosome[i], *two.chromosome[i]);

		one.valid_hash = false;
		two.valid_hash = false;

		return 0;
	}

	bool operator==(const GA_Solution_OA& solution_one, const GA_Solution_OA& solution_two)
	{
		if(solution_one.chromosome.size() != solution_two.chromosome.size())
			return 0;

		// check if the Gene Clusters are equal
		if(solution_one.chromosome == solution_two.chromosome)
			return 1;
        

		// if all the members of one tree establishment are in arbitrary trees of the other - equality
		if (solution_one.is_permutable() && solution_two.is_permutable())
		{
			set<int> weights_set_one;

			// find out how many weights (trees) there are
			for(int i = 0; i < solution_one.chromosome.size(); i ++)
            {
                int temp = solution_one.chromosome[i] -> get_ind_active_gene();
                
                if(temp != -1)
                    weights_set_one.insert(temp);
            }


			set<int> weights_set_two;

			for(int i = 0; i < solution_two.chromosome.size(); i ++)
            {
                int temp = solution_two.chromosome[i] -> get_ind_active_gene();
                
                if(temp != -1)
                    weights_set_two.insert(temp);
            }


			// each solution has to be formed by the same number of trees
			if(weights_set_one.size() != weights_set_two.size())
				return 0;


			vector<int>weights_one(weights_set_one.begin(), weights_set_one.end());
			map<int, int> adjustment_one;

            // if the 0-th tree wasn't used in this solution
            // the first tree will have index ind - weights_one[0]
			for(int i = 0; i < weights_one.size(); i ++)
				adjustment_one[weights_one[i]] = -weights_one[0];

            // check if some of the further trees was missed 
            // and adjust the indexes of the following trees
			for(int i = 1; i < weights_one.size(); i ++)
			{
				int diff = weights_one[i] - weights_one[i - 1];

				if (diff > 1)
				{
					for(int j = i; j < weights_one.size(); j ++)
						adjustment_one[weights_one[j]] -= diff;
				}
			}

            vector<int>weights_two(weights_set_two.begin(), weights_set_two.end());
			map<int, int> adjustment_two;

            // if the 0-th tree wasn't used in this solution
            // the first tree will have index ind - weights_two[0]
			for(int i = 0; i < weights_two.size(); i ++)
				adjustment_two[weights_two[i]] = -weights_two[0];

            // check if some of the further trees was missed 
            // and adjust the indexes of the following trees
			for(int i = 1; i < weights_two.size(); i ++)
			{
				int diff = weights_two[i] - weights_two[i - 1];

				if (diff > 1)
				{
					for(int j = i; j < weights_two.size(); j ++)
						adjustment_two[weights_two[j]] -= diff;
				}
			}

			// combine the indexes with the same weight into "trees"
			vector<vector<int>> trees_one(weights_one.size());
			vector<vector<int>> trees_two(weights_two.size());

			for(int i = 0; i < solution_one.chromosome.size(); i ++)
			{
				int temp = solution_one.chromosome[i] -> get_ind_active_gene();

				if(temp != -1)
					trees_one[temp + adjustment_one[temp]].push_back(i);
			}


			for(int i = 0; i < solution_two.chromosome.size(); i ++)			
			{
				int temp = solution_two.chromosome[i] -> get_ind_active_gene();
				
				if(temp != -1)
					trees_two[temp + adjustment_two[temp]].push_back(i);
			}


			for(int i = 0; i < trees_one.size(); i ++)
				sort(trees_one[i].begin(), trees_one[i].end());


			for(int i = 0; i < trees_two.size(); i ++)
				sort(trees_two[i].begin(), trees_two[i].end());


			vector<bool> full_tree_two(trees_two.size(), false);

			// for each tree A
			for(int i = 0; i < trees_one.size(); i ++)
			{
				// check if all of its members are in some other tree B
				for(int j = 0; j < trees_two.size(); j ++)
				{
					if(full_tree_two[j])
						continue;

					// exclude tree B from the further checks
					if(trees_one[i] == trees_two[j])
					{
						full_tree_two[j] = true;
						break;
					}
				}
			}


			// if there is a match to each tree from the second solution
			if(accumulate(full_tree_two.begin(), full_tree_two.end(), 0) == full_tree_two.size())
				return 1;
		}

		return 0;
	}
}