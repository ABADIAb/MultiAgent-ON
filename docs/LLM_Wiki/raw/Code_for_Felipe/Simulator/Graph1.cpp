#include "Graph.h"


using namespace NS_NBGA;

// A directed graph using
// adjacency list representation
Graph::Graph(int nV)
{
	V = nV; // set No. of vertices in graph
	adj = new list<int>[V]; // adjacency lists
}

void Graph::addEdge(int u, int v)
{
	adj[u].push_back(v); // Add v to u’s list.
}

// finds all paths from 's' to 'd'
vector<vector<int>> Graph::printAllPaths(int s, int d)
{
	// mark all the vertices as not visited
	bool* visited = new bool[V];

	// create an array to store paths
	int* path = new int[V];

	// initialize path[] as empty
	int path_index = 0;

	// initialize all vertices as not visited
	for(int i = 0; i < V; i++)
		visited[i] = false;

	// Call the recursive helper function to find and save all paths
	printAllPathsUtil(s, d, visited, path, path_index);

	return m_Paths;	
}

// a recursive function to find all paths from 'u' to 'd'.
// visited[] keeps track of vertices in current path.
// path[] stores actual vertices and path_index is current
// index in path[]
void Graph::printAllPathsUtil(int u, int d, bool visited[],
					  int path[], int& path_index)
{
	// Mark the current node and store it in path[]
	visited[u] = true;
	path[path_index] = u;
	path_index++;

	// if current vertex is same as destination, then save
    // current path[]
	if(u == d)
	{
		vector<int> temppath;
		for(int i = 0; i < path_index; i++)
			temppath.push_back(path[i]);
		m_Paths.push_back(temppath);
	}
	// if current vertex is not destination
	else 
	{
		// recur for all the vertices adjacent to current vertex
		list<int>::iterator i;
		for(i = adj[u].begin(); i != adj[u].end(); i++)
			if(!visited[*i])
				printAllPathsUtil(*i, d, visited, path, path_index);
	}

	// remove current vertex from path[] and mark it as unvisited
	path_index--;
	visited[u] = false;
}