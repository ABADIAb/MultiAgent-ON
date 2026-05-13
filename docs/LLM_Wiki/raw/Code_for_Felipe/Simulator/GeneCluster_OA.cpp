#include "GeneCluster_OA.h"

#include <cstdlib>
#include <stdexcept>
#include <iostream>

using namespace NS_NBGA;
using namespace std;

// construct a cluster with more than one gene
GeneCluster_OA :: GeneCluster_OA (int number_genes, bool active)
{
	if(number_genes < 1)
		throw invalid_argument("There must be at least 1 gene in cluster");

	num_genes = number_genes;
	always_active = active;

	active_gene_index = rand() % num_genes;
}


GeneCluster_OA :: GeneCluster_OA(const GeneCluster_OA& gc)
{
	this -> num_genes = gc.num_genes;

	this -> active_gene_index = gc.active_gene_index;
	this -> always_active = gc.always_active;
}


int GeneCluster_OA :: mutation()
{
	if(num_genes == 1)
	{
		// if the cluster was inactive, make it active
		if (active_gene_index == -1)
			active_gene_index = 0;

		// if the last gene is active, make the cluster inactive
		else if (always_active == false && active_gene_index == 0)
			active_gene_index = -1;
	}

	// turn on the other gene
    else
	{
		int bias = 0;

		// allow -1 to happen
		if (always_active == false)
			bias = 1;

		active_gene_index = rand() % (num_genes + bias) - bias;

		if (active_gene_index == num_genes)
			throw runtime_error("Mutation gone wrong");

		/*int temp = rand() % (2 * num_genes);

		if (temp >= 1.9 * num_genes)
			active_gene_index = -1;

		else if (temp < num_genes)
			active_gene_index = temp;*/
	}

    return 0;
}


// turn the cluster on and off
// turn on and not specifying the gene_ind -> reset
int GeneCluster_OA :: turn_on_off(bool on_off, int gene_ind) 
{
	// turn it on and set the required gene as active
	if (on_off == true)
	{
		if(gene_ind < num_genes)
			active_gene_index = gene_ind;

		else
			throw invalid_argument("Trying to turn on the nonexistant gene in the cluster");
	}

    // turn it off (only if it's allowed)
	else if (on_off == false && always_active == false)
		active_gene_index = -1;
    
    else if (on_off == false && always_active)
        throw invalid_argument("Not allowed to turn off this cluster");
	
	return 0;
}


// returns weight of the active gene or zero if the cluster isn't active



namespace NS_NBGA
{
	bool operator==(const GeneCluster_OA& cluster_one, const GeneCluster_OA& cluster_two)
	{
		// check that the active gene is the same
		if (cluster_one.active_gene_index != cluster_two.active_gene_index)
			return 0;

		// check that the activity mode it the same
		if (cluster_one.always_active != cluster_two.always_active)
			return 0;

		return 1;
	}

	// swap the acive_gene_index of 2 clusters
	int cross_cluster_op(GeneCluster_OA& one, GeneCluster_OA& two)
	{
		swap(one.active_gene_index, two.active_gene_index);

		return 0;
	}
}