#ifndef GA_SOLUTION_H
#define GA_SOLUTION_H

#include <vector>
#include <algorithm>
#include <fstream>
#include <string>
#include <memory>
using namespace std;

#include "GeneCluster.h"

namespace NS_NBGA
{
    class GA_Solution
    {
        // contains clusters that form the chromosome
        vector<unique_ptr<GeneCluster>> chromosome;
        
        // whether 2 solutions with permuted genes are still the same
        bool permutable;

        mutable bool valid_hash;
        mutable size_t hash_val;

        public:
			GA_Solution() {}
            
            // generate a random solution
            GA_Solution(vector<GeneCluster>& ch, bool permut);

            // generate a solution with structure ch and turn genes on-off according to genes vector
            GA_Solution(vector<GeneCluster>& ch, vector<bool> genes, bool permut);

            // generate a solution with structure ch and turn the gene in the cluster according to genes vector
            GA_Solution(vector<GeneCluster>& ch, vector<int> genes, bool permut);

            GA_Solution(const GA_Solution& sol);
            GA_Solution(GA_Solution&& sol);

            GA_Solution& operator=(const GA_Solution& sol);
            GA_Solution& operator=(GA_Solution&& sol);

			bool is_active(int index) const { return chromosome[index] -> is_active(); }
            bool is_permutable() const { return (permutable == true); }
			int get_active_ind(int index) const { return chromosome[index] -> get_ind_active_gene(); }

            int print(ofstream& file, int print_weights = 1) const;
			int mutation_op(int index) { chromosome[index] -> mutation(); valid_hash = false; return 0; };
			
            int swap_genes(int index_a, int index_b) { swap(chromosome[index_a], chromosome[index_b]); valid_hash = false; return 0; }

            class HashFunction
            {
                public:
                size_t operator()(const GA_Solution& solution) const
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

			friend int crossover_op(GA_Solution& one, GA_Solution& two, int pos);
			friend bool operator==(const GA_Solution& one, const GA_Solution& two);
    };
};

#endif