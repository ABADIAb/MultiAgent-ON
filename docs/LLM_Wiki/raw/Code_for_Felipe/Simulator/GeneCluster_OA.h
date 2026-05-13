#ifndef GENETIC_CLUSTER_OA_H
#define GENETIC_CLUSTER_OA_H

#include <vector>
using namespace std;

namespace NS_NBGA
{
    class GeneCluster_OA
	{
        // position of the active gene in the cluster
		// if non is chosen, active_gene_index = -1
		int active_gene_index;

		// active_gene_index is from 0 to num_genes - 1
		int num_genes;

		// genes can't all be 0 if true
		bool always_active;


		public:
            GeneCluster_OA() {}
			GeneCluster_OA(int number_genes, bool always_active = false);   // random gene is turned on

			GeneCluster_OA(const GeneCluster_OA& gc);

			// turn the cluster on (gene_ind specified) or off
			int turn_on_off(bool on_off, int gene_ind = 0);

			// circular shift of the active gene or choosing a random gene
			int mutation();

			int get_ind_active_gene() const { return active_gene_index; }
			int get_size() const { return num_genes; }

			bool is_active() const { return active_gene_index != -1; }
			bool is_always_active() const { return always_active == true; }

		friend int cross_cluster_op(GeneCluster_OA& one, GeneCluster_OA& two);
		friend bool operator==(const GeneCluster_OA& , const GeneCluster_OA&);
	};
};

#endif