#include "GeneCluster.h"

#include <cstdlib>
#include <stdexcept>
#include <iostream>

using namespace NS_NBGA;
using namespace std;

// construct a cluster with more than one gene
GeneCluster :: GeneCluster (int number_genes, vector<int> mutation_parts, 
					vector<int> important_mutation_parts, bool active)
{
	// check the number of genes
	if(number_genes < 1)
		throw invalid_argument("There must be at least 1 gene in cluster");

	num_genes = number_genes; // set the number of genes

	// if it is true, this gene cluster must have an active gene always
	always_active = active; 

	mutation_modes = mutation_parts; // groups of mutation

	important_mutation_modes = important_mutation_parts; // important groups of mutation

	active_gene_index = rand() % num_genes; // activate a random gene
}

// creates a new gene cluster with the parameters of another one
GeneCluster :: GeneCluster(const GeneCluster& gc)
{
	this -> num_genes = gc.num_genes;

	this -> active_gene_index = gc.active_gene_index;

	this -> always_active = gc.always_active;

	this -> mutation_modes = gc.mutation_modes;

	this -> important_mutation_modes = gc.important_mutation_modes;
}

// performs mutation on the gene cluster
int GeneCluster :: mutation()
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
		// allow -1 to happen
		if (always_active == false)
		{
			active_gene_index = rand() % (num_genes + 1);
		}

		else
		{	
			active_gene_index = rand() % num_genes;
		}	
		
	}

    return 0;
}


// turn the cluster on and off
// turn on and not specifying the gene_ind -> reset
int GeneCluster :: turn_on_off(bool on_off, int gene_ind) 
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
	{
		active_gene_index = -1;
	}
    
    else if (on_off == false && always_active)
	{
        throw invalid_argument("Not allowed to turn off this cluster");
	}
	
	return 0;
}

namespace NS_NBGA
{
	bool operator==(const GeneCluster& cluster_one, const GeneCluster& cluster_two)
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
	int cross_cluster_op(GeneCluster& one, GeneCluster& two)
	{
		swap(one.active_gene_index, two.active_gene_index);

		return 0;
	}
}