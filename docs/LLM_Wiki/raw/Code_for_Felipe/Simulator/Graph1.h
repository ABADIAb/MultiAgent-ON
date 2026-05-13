#ifndef GRAPH_H
#define GRAPH_H

#include <iostream>
#include <list>
#include <vector>
//#include "TypeDef.h"

using namespace std;

namespace NS_NBGA {

	class Graph {

		public:
			Graph(int nV);

			// A recursive function used by printAllPaths()
			void printAllPathsUtil(int u, int d, bool visited[], int path[], int& path_index);

			// function for adding edge to the graph
			void addEdge(int u, int v);

			// finds all paths from 's' to 'd'
			vector<vector<int>> printAllPaths(int s, int d);
		
		public:

			int V; // No. of vertices in graph
			list<int>* adj; // Pointer to an array containing adjacency lists
			vector<vector<int> > m_Paths; // 2d vector for saving all possible paths btw s and d 
	};
};

#endif