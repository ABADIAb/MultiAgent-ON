#ifndef GA_SOLUTION_OA_H
#define GA_SOLUTION_OA_H

#include <vector>
#include <algorithm>
#include <fstream>
#include <string>
#include <memory>
using namespace std;

#include "GeneCluster_OA.h"

namespace NS_NBGA
{
    class GA_Solution_OA
    {
        // contains clusters that form the chromosome
        vector<unique_ptr<GeneCluster_OA>> chromosome;
        
        // whether 2 solutions with permuted genes are still the same
        bool permutable;

        mutable bool valid_hash;
        mutable size_t hash_val;

        mutable float cost;

        public:
			GA_Solution_OA() {}
            
            // generate a random solution
            GA_Solution_OA(vector<GeneCluster_OA>& ch, bool permut);

            // generate a solution with structure ch and turn genes on-off according to genes vector
            GA_Solution_OA(vector<GeneCluster_OA>& ch, vector<bool> genes, bool permut);

            // generate a solution with structure ch and turn the gene in the cluster according to genes vector
            GA_Solution_OA(vector<GeneCluster_OA>& ch, vector<int> genes, bool permut);

            GA_Solution_OA(const GA_Solution_OA& sol);
            GA_Solution_OA(GA_Solution_OA&& sol);

            GA_Solution_OA& operator=(const GA_Solution_OA& sol);
            GA_Solution_OA& operator=(GA_Solution_OA&& sol);

			bool is_active(int index) const { return chromosome[index] -> is_active(); }
            bool is_permutable() const { return (permutable == true); }
			int get_active_ind(int index) const { return chromosome[index] -> get_ind_active_gene(); }

            int print(ofstream& file, int print_weights = 1) const;
			int mutation_op(int index) { chromosome[index] -> mutation(); valid_hash = false; return 0; };
			
            int swap_genes(int index_a, int index_b) { swap(chromosome[index_a], chromosome[index_b]); valid_hash = false; return 0; }

            int set_cost(float c) const { cost = c; return 0; }
            float get_cost() const { return cost; }

            class HashFunction
            {
                public:
                size_t operator()(const GA_Solution_OA& solution) const
                {
                    if (solution.valid_hash == false)
                    {
                        string str;
                        for(int i = 0; i < solution.chromosome.size(); i++)
                            str += to_string(solution.get_active_ind(i));

                        solution.hash_val = hash<string>()(str);
                        solution.valid_hash = true;
                    }

                    return solution.hash_val;
                }
            };

			friend int crossover_op(GA_Solution_OA& one, GA_Solution_OA& two, int pos);
			friend bool operator==(const GA_Solution_OA& one, const GA_Solution_OA& two);
    };
};

#endif