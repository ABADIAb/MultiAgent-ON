#include <assert.h>

#include <cstring>
#include <float.h>
#include <numeric>

#include <bits/stdc++.h>
#include <sstream>
#include <algorithm> 
#include <thread> 

#include <utility> // std::pair
#include <stdexcept> // std::runtime_error

#include "Network.h"


using namespace std;
using namespace NS_NBGA;

int max_possible_throughput(double SNR_dB)
{
	int margin = 2;

	if(SNR_dB < 6.7 + margin)
		return 0;

	else if (SNR_dB >= 6.7 + margin && SNR_dB < 10.8 + margin)
		return 100;

	else if (SNR_dB >= 10.8 + margin && SNR_dB < 13.2 + margin)
		return 150;

	else if (SNR_dB >= 13.2 + margin && SNR_dB < 16.2 + margin)
		return 200;

	else if (SNR_dB >= 16.2 + margin && SNR_dB < 19 + margin)
		return 250;

	else if (SNR_dB >= 19 + margin)
		return 300;
}


bool ari_debug = false;

Network::Network()
{
}

bool Network::initialize(const char *pInputFile, int objective_input, int NumberLambdas, int max_number_gen,  float years_input, const char* result_file_name)
{
	// this function initializes the netwrok according to the input parameters
    cout << "initializing the network" << endl;
    
	// set the main parameters from input
    number_lambdas = NumberLambdas;
	max_number_generation = max_number_gen;
	years = years_input;
	objective = objective_input;
	result_file_n = result_file_name;

	// read the topology file
	// read and save the nodes
	// read and save the uni fibers
	// read and save the connection requests
    if (!readTopo(pInputFile))
    {
		// could not read the topology file and return with a false value
        cerr << "- error reading topo file " << pInputFile << endl;
        return false;
    }

	// set the total number of connection requests
	// note that it is different from the one indicated in the input topology file
	// since in the vector we add 2 connection requests for every protected connection 
	number_connection_requests = connection_requests.size();

	// get and save all possible candidate paths for all possible node-pairs (src, dst) in the topology
	getPaths();

	// find the correspondig candidate paths vector for each connection request 
	mapRequestToPair();

	//GA_initializer1(800);

	// if we get here means there was no problem in the initialization so return with a true value
    return true; 
}

bool Network::readTopo(const char *pInputFile)
{
    cout << "opening the input file: " << pInputFile << endl;

	// variable for keeping the status
    bool bSuccess = true;

	// attempt to open the input file
    ifstream fin(pInputFile, ios::in);
	
	// check if it was successful or not
    if (fin.fail()) 
    {
		// if it failes return with a false value
		cout << "Opening the input file failed!" << endl;
		return false;
	}

	// if we get here means input file opened successfully
	// attempt to read the opened file
    bSuccess = readTopoHelper(fin);

	// close the opened file
    fin.close();

	// return status of reading the file 
	return bSuccess;
}

bool Network::readTopoHelper (ifstream &fin)
{
    cout << "reading parameters from the input file: " << endl;

	// define variables for detecting the input file structure
	const int MAX_LINE_LENGTH = 2048;
	const char *pTopoNodesCount = "NumberOfTopoNodes = ";
	const char *pTopoNodesHead = "TopoNodes";
	const char *pTopoNodeFormat = "%u, %u";
	const char *pUniFiberCount = "NumberOfUniFibers = ";
	const char *pUniFiberHead = "UniFibers";
	const char *pUniFiberFormat = "%u, %u, %u, %u, %u";
	const char *pCrequestsCount = "NumberOfCrequests = ";
	const char *pCrequestsHead = "Crequests";
	const char *pCrequestFormat = "%u, %u, %u, %u, %u, %u";
	const char cStartDelimiter = '<';
	const char cEndDelimiter = '>';

	///*
	//added by MEM regarding the CandidateLocations for placing Optical Amplifiers
	const char *pNumCandLoc = "NumberOfCandLoc = ";	//number of candidate locations in the network
	const char *pNumCandLocHead = "CandidateLocations";  
	const char *pNumCandLocFormat = "%u, %u, %u, %u, %f, %f, %u";	//format of the CandidateLocations given as input

	int nCandLoc = 0; 
	//end of added by MEM
	//*/

	char pBuf[MAX_LINE_LENGTH + 1];

	// read number of nodes written in the file
	int nTopoNodes = 0;
    while (fin.getline(pBuf, MAX_LINE_LENGTH) && !strstr(pBuf, pTopoNodesCount)){}
	sscanf(pBuf, "NumberOfTopoNodes = %d", &nTopoNodes);
	number_nodes = nTopoNodes;
	assert(fin && (nTopoNodes > 0));
	cout << "number of nodes: " << nTopoNodes << endl;

	// read number of unidirectional fibers written in the file
	int nUniFibers = 0;
	while (fin.getline(pBuf, MAX_LINE_LENGTH) && !strstr(pBuf, pUniFiberCount)){}
	sscanf(pBuf, "NumberOfUniFibers = %d", &nUniFibers);
	number_uni_fibers = nUniFibers;
	assert(fin && (nUniFibers > 0));
	cout << "number of unidirectional fibers: " << nUniFibers << endl;

	// read number of connection requests written in the file
	int nCrequests = 0;
	while (fin.getline(pBuf, MAX_LINE_LENGTH) && !strstr(pBuf, pCrequestsCount)){}
	sscanf(pBuf, "NumberOfCrequests = %d", &nCrequests);
	assert(fin && (nCrequests > 0));
	cout << "number of connection requests: " << nCrequests << endl;

	///*
	//added by MEM
	//read the number of the candidate locations
	while (fin.getline(pBuf, MAX_LINE_LENGTH) 
		&& !strstr(pBuf, pNumCandLoc)) {
		NULL;
	}
	sscanf(pBuf, "NumberOfCandLoc = %d", &nCandLoc);
	numcandloc = nCandLoc; 
	assert(fin && (nCandLoc > 0));
	//end of added by MEM
	//*/ 
	
	// read the set of nodes and add each class instance to the vector of nodes
	while (fin.getline(pBuf, MAX_LINE_LENGTH) && !strstr(pBuf, pTopoNodesHead)){}
	assert(fin);
    int nCount = 0;
	int nNodeId, nNodeCheck;
	while ((nCount < nTopoNodes) && fin.getline(pBuf, MAX_LINE_LENGTH, cStartDelimiter)) 
    {
		fin.getline(pBuf, MAX_LINE_LENGTH, cEndDelimiter);
		sscanf(pBuf, pTopoNodeFormat, &nNodeId, &nNodeCheck);
		addTopoNode(nNodeId, nNodeCheck);
		nCount++;
	}

    // read the set of unidirectional fibers and add each class instance to the vector of uni_fibers
	while (fin.getline(pBuf, MAX_LINE_LENGTH) && !strstr(pBuf, pUniFiberHead)){}	
	assert(fin);
	nCount = 0;
	int nFiberId, nSrc, nDst, nCapacity, nLength;
	while ((nCount < nUniFibers) && fin.getline(pBuf, MAX_LINE_LENGTH, cStartDelimiter)) 
    {
		fin.getline(pBuf, MAX_LINE_LENGTH, cEndDelimiter);
		sscanf(pBuf, pUniFiberFormat, &nFiberId, &nSrc, &nDst, &nCapacity, &nLength);
		addUniFiber(nFiberId, nSrc, nDst, nCapacity, nLength);
		nCount++;
	}

	// read the set of connection requests and add each class instance to the vector of connection_requests
	while (fin.getline(pBuf, MAX_LINE_LENGTH) && !strstr(pBuf, pCrequestsHead)){}
	assert(fin);
	nCount = 0;
	int nConnectionId, nConnectionSrc, nConnectionDst, nConnectionCapacity, nProtection, nRoutingType;
	while ((nCount < nCrequests) && fin.getline(pBuf, MAX_LINE_LENGTH, cStartDelimiter)) 
    {
		fin.getline(pBuf, MAX_LINE_LENGTH, cEndDelimiter);
		sscanf(pBuf, pCrequestFormat, &nConnectionId, &nConnectionSrc, &nConnectionDst, &nConnectionCapacity, &nProtection, &nRoutingType);
		addConnectionRequest(nConnectionId, nConnectionSrc, nConnectionDst, nConnectionCapacity, nProtection, nRoutingType);
		nCount++;
	}

	// Ari commented

	ofstream InitFile;
	// for the baseline
	//baseline_mode = true;
	if(baseline_mode)
	{
		InitFile.open("OA_GA_init.txt", ios::trunc);
	 	InitFile << "Initial placement 0" << endl;
	 	InitFile << "<";
	}

	//added by MEM
	nCount = 0;
	int nCandId, nCandFiberId, nCandLength, nCandInd, nCandType;
	//bool nCandInd;
	double nCandGain, nCandNF; 
	cout<< "Number of cand locs "<<nCandLoc<<endl;
	while ((nCount < nCandLoc) && fin.getline(pBuf, MAX_LINE_LENGTH, cStartDelimiter)) 
	{//&& fin.getline(pBuf, MAX_LINE_LENGTH, cStartDelimiter) 
		fin.getline(pBuf, MAX_LINE_LENGTH, cEndDelimiter);
		sscanf(pBuf, pNumCandLocFormat, 
		&nCandId, &nCandFiberId, &nCandLength, &nCandInd, &nCandGain, &nCandNF, &nCandType);

		// Ari commented
		if (baseline_mode)
		{
		 	if (nCandType == 1 || nCandType == 3 || (nCandType == 2 && (nCandLength % 80) == 0) )
		 		InitFile << nCandId << "; ";
		}
		
		addOaLoc(nCandId, nCandFiberId, nCandLength, nCandInd, nCandGain, nCandNF, nCandType);
		//int oa = OAPlacement();
		nCount++;
	}

	// Ari commented
	if(baseline_mode)
	{
		InitFile << ">";
		InitFile.close();
	}

	//baseline_mode = false;
	return true;
}

void Network::addTopoNode(int nNodeID, int nNodecheck)
{
	// creates a node instance according to the input parameters
	// and add it to the vector of nodes
	// this function is used by the readTopoHelper
    nodes.push_back(new Node(nNodeID, nNodecheck ));
}

void Network::addUniFiber(int nFiberId, int nSrc, int nDst, float nCapacity, int nLength)
{
	// creates an unidirectional fiber instance according to the input parameters
	// and add it to the vector of uni_fibers
	// this function is used by the readTopoHelper
	Unifiber* new_fiber = new Unifiber(nFiberId, nSrc, nDst, nCapacity, nLength);
	vector<Node*>::const_iterator node_itr;
	
	for (node_itr = nodes.begin(); node_itr != nodes.end(); node_itr++) 
	{
		if ((*node_itr)->getID() == nSrc / 100)
		{
			new_fiber->src_node = *node_itr;
		}
		if ((*node_itr)->getID() == nDst / 100)
		{
			new_fiber->dst_node = *node_itr;
		}
	}	

	for (node_itr = nodes.begin(); node_itr != nodes.end(); node_itr++) 
	{
		if ((*node_itr)->getID() == nSrc / 100)
		{
			(*node_itr)->out_fibers.push_back(new_fiber);
		}
		if ((*node_itr)->getID() == nDst / 100)
		{
			(*node_itr)->in_fibers.push_back(new_fiber);
		}
	}
    uni_fibers.push_back(new_fiber);
}

void Network::addConnectionRequest(int nConnectionId, int nSrc, int nDst, float nCapacity, int nProtection, int nRoutingType)
{
	// creates a connection request instance according to the input parameters
	// and add it to the vector of connection_requests
	// this function is used by the readTopoHelper

	// if the connection is not protected add just one instance
    if(nProtection == 0)
	{
		connection_requests.push_back(new Connection(nConnectionId, nSrc, nDst, nCapacity, 0, nRoutingType));
	}

	// if the connection is protected add two instances
    else if(nProtection == 1)
	{
		connection_requests.push_back(new Connection(nConnectionId, nSrc, nDst, nCapacity, 1, nRoutingType));
		connection_requests.push_back(new Connection(nConnectionId, nSrc, nDst, nCapacity, 2, nRoutingType));
	}
}

void Network::getPaths()
{

	vector<int> nodes_temp1;
	/*
	this function finds all possible candidate paths for each possible node-pair
	*/
   

	// generate all possible node-pairs in the topology
	// and save an instance for each in vector of node_pair_requests
	// for example for a 3-nodes topology all possible node-pairs are:
	// (node1->node2), (node1->node3), (node2->node3)
	vector<Node*>::const_iterator node_itr1;
	vector<Node*>::const_iterator node_itr2;
    int pair_id = 0;
	for (node_itr1 = nodes.begin(); node_itr1 != nodes.end(); node_itr1++) 
	{
		for (node_itr2 = nodes.begin(); node_itr2 != nodes.end(); node_itr2++)
		{
			if ((*node_itr1)->getID() != (*node_itr2)->getID())
			{
				int pair_src = (*node_itr1)->getID();
				int pair_dst = (*node_itr2)->getID();
				
				for(auto conn_itr = connection_requests.begin(); conn_itr != connection_requests.end(); conn_itr++)
				{
					int route = (*conn_itr) -> RoutingType();
					
					if ((*conn_itr)->getSrcID() / 100 == pair_src && (*conn_itr)->getDstID() / 100 == pair_dst)
					{
					
						node_pair_requests.push_back(new Connection(pair_id, pair_src, pair_dst, 0, false, route));
						pair_id += 1;
						break;

					}
				}
			}
		}
	}

	vector<vector<int>> temp_paths2;
	// go through node-pairs and find all possible paths related to that node-pair and save them 
	vector<Connection*>::const_iterator node_pair_itr;
	for (node_pair_itr = node_pair_requests.begin(); node_pair_itr != node_pair_requests.end(); node_pair_itr++) 
	{
		int roadm_vertices = 2;
		int roadm_total_vertices = number_nodes * roadm_vertices + 2;
		ofstream roadm_graph_file ("Yen_graph_roadm", std::ios_base::out);
		roadm_graph_file << roadm_total_vertices << endl << endl;
		int src_vertice = roadm_total_vertices - 2;
		int dst_vertice = roadm_total_vertices - 1;
		vector<Node*>::const_iterator node_itr;
		for (node_itr = nodes.begin(); node_itr != nodes.end(); node_itr++) 
		{
			int roadm_left, roadm_right;
			roadm_left = ((*node_itr)->getID() - 1) * roadm_vertices;
			roadm_right = roadm_left + 1;

			if (!( ((*node_pair_itr)->getSrcID() == (*node_itr)->getID()) ||
				   ((*node_pair_itr)->getDstID() == (*node_itr)->getID())))
			{
				//m_Graph.addEdge(start + 5, start + 6);
				//m_Graph.addEdge(start + 6, start + 5);
				roadm_graph_file << roadm_left << " " << roadm_right << " " << "1" << endl;
				roadm_graph_file << roadm_right << " " << roadm_left << " " << "1" << endl;
			}
			else if ((*node_pair_itr)->getSrcID() == (*node_itr)->getID())
			{
				roadm_graph_file << roadm_left << " " << src_vertice << " " << "0" << endl;
				roadm_graph_file << src_vertice << " " << roadm_left << " " << "0" << endl;
				roadm_graph_file << roadm_right << " " << src_vertice << " " << "0" << endl;
				roadm_graph_file << src_vertice << " " << roadm_right << " " << "0" << endl;
			}
			else if ((*node_pair_itr)->getDstID() == (*node_itr)->getID())
			{
				roadm_graph_file << roadm_left << " " << dst_vertice << " " << "0" << endl;
				roadm_graph_file << dst_vertice << " " << roadm_left << " " << "0" << endl;
				roadm_graph_file << roadm_right << " " << dst_vertice << " " << "0" << endl;
				roadm_graph_file << dst_vertice << " " << roadm_right << " " << "0" << endl;
			}

		}
		// now we need to add the edges corresponding to fibers
		vector<Unifiber*>::const_iterator unifiber_itr;
		for (unifiber_itr = uni_fibers.begin(); unifiber_itr != uni_fibers.end(); unifiber_itr++) 
		{
			int edge_src = 0;
			int edge_dst = 0;

			// roadm IDs are coded as (node id * 100) + 49 for roadm left or (node id * 100) + 59 for roadm right
			// for example 149 is roadm left node1 and 359 is roadm right node3

			// get the fiber source roadm and fiber source node
			int fiber_src_roadm = (*unifiber_itr)->getSrcId() % 100;
			int fiber_src_node = (*unifiber_itr)->getSrcId() / 100;

			// get the fiber destination roadm and fiber destination node
			int fiber_dst_roadm = (*unifiber_itr)->getDstId() % 100;
			int fiber_dst_node = (*unifiber_itr)->getDstId() / 100;

			// map roadms to their corresponding vertice in the graph
			if (fiber_src_roadm == 49)
				edge_src = ((fiber_src_node - 1) * roadm_vertices);
			else if (fiber_src_roadm == 59)
				edge_src = ((fiber_src_node - 1) * roadm_vertices) + 1;

			if (fiber_dst_roadm == 49)
				edge_dst = ((fiber_dst_node - 1) * roadm_vertices);
			else if (fiber_dst_roadm == 59)
				edge_dst = ((fiber_dst_node - 1) * roadm_vertices) + 1;

			// add the edge
			//m_Graph.addEdge(edge_src, edge_dst);
			roadm_graph_file << edge_src << " " << edge_dst<< " " << "1" << endl;
		}

		vector<vector<int> > temp_paths;

		Graph my_graph1("Yen_graph_roadm");

		YenTopKShortestPathsAlg yenAlg_roadms(my_graph1, my_graph1.get_vertex(src_vertice),
			my_graph1.get_vertex(dst_vertice));

		int i = 0;
		while(yenAlg_roadms.has_next())
		{
			vector <int> shortest_path;
			vector <int> shortest_path_actual;
			shortest_path = yenAlg_roadms.next()->get_path_ids();
			for (int j = 0 ; j < shortest_path.size() ; j++)
			{
				int actualId;
				if (shortest_path[j] == src_vertice)
				{
					actualId = (*node_pair_itr)->getSrcID() * 100;
				}
				else if(shortest_path[j] == dst_vertice)
				{
					actualId = (*node_pair_itr)->getDstID() * 100;
				}

				else if(shortest_path[j] % roadm_vertices == 0)
				{
					actualId = (((shortest_path[j] / roadm_vertices) + 1) * 100) + 49;
				}
				else if(shortest_path[j] % roadm_vertices == 1)
				{
					actualId = (((shortest_path[j] / roadm_vertices) + 1) * 100) + 59;
				}

				// we add the actual ID to the corresponding path in the corresponding page of the overall 3d memory
				// (*node_pair_itr)->getId() is the corresponding page
				// i is the corresponding path
				shortest_path_actual.push_back(actualId);	
			}

			temp_paths.push_back(shortest_path_actual);
			++ i;
			if (i == 2)
				break;
		}
	
		temp_paths2 = temp_paths;	

		vector <Node*>::const_iterator node_itr3;
		vector <Unifiber*>::const_iterator fiber_itr3;
		
		vector<vector<int>> all_concat_paths;
		vector<vector<int>> all_concat_paths_100;
		for(int k = 0 ; k < temp_paths2.size(); k++)
		{
			vector <int> node_in_shortestpath;
			vector <Unifiber*> new_fibers;
			for (int l = 0 ; l < temp_paths2[k].size(); l++)
			{
				for (node_itr3 = nodes.begin(); node_itr3 != nodes.end(); node_itr3++)
				{
					if(temp_paths2[k][l]/100  == (*node_itr3)->getID())
					{
						node_in_shortestpath.push_back((*node_itr3)->getID());	
						//cout<<(*node_itr3)->getID()<< " ";
					}
				}
				if (l < temp_paths2[k].size()-1)
				{
					for (fiber_itr3 = uni_fibers.begin(); fiber_itr3 != uni_fibers.end(); fiber_itr3++)
					{
						if (temp_paths2[k][l] == (*fiber_itr3)->getSrcId() && temp_paths2[k][l+1] == (*fiber_itr3)->getDstId())
						{
							new_fibers.push_back((*fiber_itr3));
						}
						else if (temp_paths2[k][l+1] == (*fiber_itr3)->getSrcId() && temp_paths2[k][l] == (*fiber_itr3)->getDstId())
						{
							new_fibers.push_back((*fiber_itr3));
						}
					}

				}
			
			}
			vector <Node*> new_nodes; 
			sort(node_in_shortestpath.begin(), node_in_shortestpath.end());
			node_in_shortestpath.erase(unique (node_in_shortestpath.begin(),node_in_shortestpath.end()),node_in_shortestpath.end());
			for (int i = 0; i < node_in_shortestpath.size(); i++)
			{
				for (node_itr3 = nodes.begin(); node_itr3 != nodes.end(); node_itr3++)
				{
					if(node_in_shortestpath[i] == (*node_itr3)->getID())
					{
						new_nodes.push_back((*node_itr3));
					}
				}
			}
			int node_vertices = 7;
		
			//int route_check = (*node_pair_itr)->RoutingType();

			ofstream graph_file("Yen_graph", std::ios_base::out);
			

			// find how many graph nodes we need
			int TotalVertices = calculateTotalVertices(node_vertices, new_nodes);
			
			graph_file << TotalVertices << endl << endl;
			
			// now we need to add the edges of the graph
			// go through the nodes and add the edges accordingly
			vector<Node*>::const_iterator node_itr;
			
			for (node_itr = new_nodes.begin(); node_itr != new_nodes.end(); node_itr++) 
			{	
				
				// find the starting vertice for each network node
				// each network node needs 7 vertices and the first one is the starting vertice
				// for a 3-nodes topology 0, 7, 14 are the starting vertices for node 1, 2, 3 respectively
				
				int start;
				start = ((*node_itr)->getID() - 1) * node_vertices;	
				if((*node_itr)->getNodeCheck() == 1)
				{	
						
					// add two edges (because the links are bidirectional) 
					// between "main vertice of the node" and "10G left vetice of the node"
					// note that start + 1 is the vertice corresponding to 10G left
					//m_Graph.addEdge(start, start + 1);
					//m_Graph.addEdge(start + 1, start);
					graph_file << start << " " << start + 1 << " " << "1" << endl;
					graph_file << start + 1 << " " << start << " " << "1" << endl;
					// add two edges (because the links are bidirectional) 
					// between "main vertice of the node" and "10G right vetice of the node"
					// note that start + 2 is the vertice corresponding to 10G right
					//m_Graph.addEdge(start, start + 2);
					//m_Graph.addEdge(start + 2, start);
					graph_file << start << " " << start + 2 << " " << "1" << endl;
					graph_file << start + 2 << " " << start << " " << "1" << endl;


					// add two edges (because the links are bidirectional) 
					// between "10G left vetice of the node" and "roadm left vetice of the node"
					// note that start + 1 is the vertice corresponding to 10G left
					// and start + 5 is the vertice corresponding to roadm left
					//m_Graph.addEdge(start , start + 3);
					//m_Graph.addEdge(start + 3, start );
					graph_file << start << " " << start + 3 << " " << "1" << endl;
					graph_file << start + 3 << " " << start << " " << "1" << endl;

					// add two edges (because the links are bidirectional) 
					// between "tpd card left vetice of the node" and "roadm left vetice of the node"
					// note that start + 3 is the vertice corresponding to tpd card left
					// and start + 5 is the vertice corresponding to roadm left
					//m_Graph.addEdge(start , start + 4);
					//m_Graph.addEdge(start + 4, start );
					graph_file << start << " " << start + 4 << " " << "1" << endl;
					graph_file << start + 4 << " " << start << " " << "1" << endl;

					// add two edges (because the links are bidirectional) 
					// between "tpd card left vetice of the node" and "roadm left vetice of the node"
					// note that start + 3 is the vertice corresponding to tpd card left
					// and start + 5 is the vertice corresponding to roadm left
					//m_Graph.addEdge(start + 1 , start + 5);
					//m_Graph.addEdge(start + 5, start + 1 );
					graph_file << start + 1 << " " << start + 5 << " " << "1" << endl;
					graph_file << start + 5 << " " << start + 1 << " " << "1" << endl;

					// add two edges (because the links are bidirectional) 
					// between "tpd card left vetice of the node" and "roadm left vetice of the node"
					// note that start + 3 is the vertice corresponding to tpd card left
					// and start + 5 is the vertice corresponding to roadm left
					//m_Graph.addEdge(start + 3 , start + 5);
					//m_Graph.addEdge(start + 5, start + 3 );

					graph_file << start + 3 << " " << start + 5 << " " << "1" << endl;
					graph_file << start + 5 << " " << start + 3 << " " << "1" << endl;

					// add two edges (because the links are bidirectional) 
					// between "tpd card left vetice of the node" and "roadm left vetice of the node"
					// note that start + 3 is the vertice corresponding to tpd card left
					// and start + 5 is the vertice corresponding to roadm left
					//m_Graph.addEdge(start + 2 , start + 6);
					//m_Graph.addEdge(start + 6, start + 2 );
					graph_file << start + 2 << " " << start + 6 << " " << "1" << endl;
					graph_file << start + 6 << " " << start + 2 << " " << "1" << endl;

					// add two edges (because the links are bidirectional) 
					// between "tpd card left vetice of the node" and "roadm left vetice of the node"
					// note that start + 3 is the vertice corresponding to tpd card left
					// and start + 5 is the vertice corresponding to roadm left
					//m_Graph.addEdge(start + 4 , start + 6);
					//m_Graph.addEdge(start + 6, start + 4 );
					graph_file << start + 4 << " " << start + 6 << " " << "1" << endl;
					graph_file << start + 6 << " " << start + 4 << " " << "1" << endl;
				}
				// add two edges (because the links are bidirectional) 
				// between "roadm left vetice of the node" and "roadm right vetice of the node"
				// if the node is not the main source or the main destination (terminal nodes)
				// for example if we are considering the node-pair (1, 3):
				// for node1 and node3, we don't consider the edge btw roadms
				// but for node2, we consider the edge btw roadms since it is an intermediate node 
				// note that start + 5 is the vertice corresponding to roadm left
				// and start + 6 is the vertice corresponding to roadm right
				if (!( ((*node_pair_itr)->getSrcID() == (*node_itr)->getID()) ||
					((*node_pair_itr)->getDstID() == (*node_itr)->getID())))
				{
					//m_Graph.addEdge(start + 5, start + 6);
					//m_Graph.addEdge(start + 6, start + 5);
					graph_file << start + 5 << " " << start + 6 << " " << "1" << endl;
					graph_file << start + 6 << " " << start + 5 << " " << "1" << endl;
				}

			}
			// now we need to add the edges corresponding to fibers
			vector<Unifiber*>::const_iterator unifiber_itr;
			for (unifiber_itr = new_fibers.begin(); unifiber_itr != new_fibers.end(); unifiber_itr++) 
			{
				int edge_src = 0;
				int edge_dst = 0;

				// roadm IDs are coded as (node id * 100) + 49 for roadm left or (node id * 100) + 59 for roadm right
				// for example 149 is roadm left node1 and 359 is roadm right node3

				// get the fiber source roadm and fiber source node
				int fiber_src_roadm = (*unifiber_itr)->getSrcId() % 100;
				int fiber_src_node = (*unifiber_itr)->getSrcId() / 100;

				// get the fiber destination roadm and fiber destination node
				int fiber_dst_roadm = (*unifiber_itr)->getDstId() % 100;
				int fiber_dst_node = (*unifiber_itr)->getDstId() / 100;			

				// map roadms to their corresponding vertice in the graph
				if (fiber_src_roadm == 49)
					edge_src = ((fiber_src_node - 1) * node_vertices) + 5;
				else if (fiber_src_roadm == 59)
					edge_src = ((fiber_src_node - 1) * node_vertices) + 6;

				if (fiber_dst_roadm == 49)
					edge_dst = ((fiber_dst_node - 1) * node_vertices) + 5;
				else if (fiber_dst_roadm == 59)
					edge_dst = ((fiber_dst_node - 1) * node_vertices) + 6;
				

				// add the edge
				//m_Graph.addEdge(edge_src, edge_dst);
				graph_file << edge_src << " " << edge_dst<< " " << "1" << endl;
					
					
			}

			// map pair's source id and pair's destination id to their corresponding vertice in the graph
			int src = ((*node_pair_itr)->getSrcID() - 1) * node_vertices;
			int dst = ((*node_pair_itr)->getDstID() - 1) * node_vertices;

			// allocate a 2d memory for current node pair and add it to the overall 3d memory (ext_candidate_paths)
			

			// get all possible paths for the current node pair
			vector<vector<int> > temp_paths;
			vector<vector<int> > temp_paths_100;

			Graph my_graph("Yen_graph");

			YenTopKShortestPathsAlg yenAlg(my_graph, my_graph.get_vertex(src),
				my_graph.get_vertex(dst));

			int i = 0;
			while(yenAlg.has_next())
			{
				vector <int> shortest_path;
				vector <int> shortest_path_actual;
				shortest_path = yenAlg.next()->get_path_ids();
				// now for each item in the path we find the actual ID
				for (int j = 0 ; j < shortest_path.size() ; j++)
				{
					/*
					actual ID is a number that we chose for each component (roadms, tpd cards, 10G interfaces, ...)
					the format is (node id * 100) + x
					x is 91 for 10G interface left
					x is 95 for 10G interface right
					note that:
					- 91 represents all four 10G interfaces of OTU2 left side, later we expand it to 4 different IDs (91, 92, 93, 94)
					- 95 represents all four 10G interfaces of OTU2 right side, later we expand it to 4 different IDs (95, 96, 97, 98)
					- the reason is reducing number of candidate paths

					x is 47 for tpd card left
					x is 48 for tpd card right

					x is 49 for roadm left
					x is 59 for roadm right

					for example 248 is tpd right of node2 and 391 is 10G interface left node3
					*/
					int actualId;
					if (shortest_path[j] % node_vertices == 0)
					{
						actualId = ((shortest_path[j] / node_vertices) + 1) * 100;
					}
					else if(shortest_path[j] % node_vertices == 1)
					{
						actualId = (((shortest_path[j] / node_vertices) + 1) * 100) + 47;
					}
					else if(shortest_path[j] % node_vertices == 2)
					{
						actualId = (((shortest_path[j] / node_vertices) + 1) * 100) + 48;
					}
					else if(shortest_path[j] % node_vertices == 3)
					{
						actualId = (((shortest_path[j] / node_vertices) + 1) * 100) + 91;
					}
					else if(shortest_path[j] % node_vertices == 4)
					{
						actualId = (((shortest_path[j] / node_vertices) + 1) * 100) + 95;
					}
					else if(shortest_path[j] % node_vertices == 5)
					{
						actualId = (((shortest_path[j] / node_vertices) + 1) * 100) + 49;
					}
					else if(shortest_path[j] % node_vertices == 6)
					{
						actualId = (((shortest_path[j] / node_vertices) + 1) * 100) + 59;
					}

					// we add the actual ID to the corresponding path in the corresponding page of the overall 3d memory
					// (*node_pair_itr)->getId() is the corresponding page
					// i is the corresponding path
					shortest_path_actual.push_back(actualId);	
				}
				bool flag_check = true;
				bool flag_check_100 = true;
				int drop_count = 0;

				// go through each component of the path
				for( int k = 0 ; k < shortest_path_actual.size() - 1; k++)
				{
					// if it is end node of a lightpath, (100, 200, 300, ...)
					if(shortest_path_actual[k] % 100 == 0)
					{
						// find the other end
						drop_count ++;
						int start_index = k+1;
						int x = start_index + 1;
						while(shortest_path_actual[x] % 100 == 49 || shortest_path_actual[x] % 100 == 59)
						{
							x++;
						}
						int end_index = x;

						// if it starts with tpd and the other end is not a tpd this is not a valid path
						if((shortest_path_actual[start_index] % 100 == 47 || shortest_path_actual[start_index] % 100 == 48) &&
							!(shortest_path_actual[end_index] % 100 == 47 || shortest_path_actual[end_index] % 100 == 48))
						{
							flag_check = false;
							//break;
						}

						// if it starts with 10G interface and the other end is not a 10G interface this is not a valid path
						if((shortest_path_actual[start_index] % 100 == 91 || shortest_path_actual[start_index] % 100 == 95) &&
							!(shortest_path_actual[end_index] % 100 == 91 || shortest_path_actual[end_index] % 100 == 95))
						{
							flag_check = false;
							//break;
						}

						if((shortest_path_actual[start_index] % 100 == 91 || shortest_path_actual[start_index] % 100 == 95) &&
							(shortest_path_actual[end_index] % 100 == 91 || shortest_path_actual[end_index] % 100 == 95))
						{
							flag_check_100 = false;
							//break;
						}
							
					}
				}

				int i = 0;
				// if the path was correct, add it to the new temp memory
				/*if (flag_check == true)
				{
					temp_paths.push_back(shortest_path_actual);
					++ i;
					if (flag_check_100 == true)
					{
						temp_paths_100.push_back(shortest_path_actual);
					}
					//if (i > 100)
					//	break;
				}*/
				if (flag_check == true)
				{
					temp_paths.push_back(shortest_path_actual);
					++ i;
					if(drop_count < 2)
					{
						if (flag_check_100 == true)
						{
							temp_paths_100.push_back(shortest_path_actual);
						}
						
					}
					
					if (drop_count >= 2)
				 		break;
				}
			}
			all_concat_paths.insert(all_concat_paths.end(), temp_paths.begin(), temp_paths.end());
			all_concat_paths_100.insert(all_concat_paths_100.end(), temp_paths_100.begin(), temp_paths_100.end());

			graph_file.close();
	
		}	
		ext_candidate_paths_10.push_back(all_concat_paths);
		ext_candidate_paths_100.push_back(all_concat_paths_100);
	}
		
		
	// for each existing candidate path extract the needed lightpaths and save them in ext_candidate_LPs
	// ext_candidate_LPs is a 3d vector as same size as ext_candidate_paths
	// each row of each page of ext_candidate_LPs corresponds to the same row and same page of the ext_candidate_pahs
	// Example:
	// set of needed lightpaths for path (100,195,159,249,291,200,295,259,349,391,300) is
	// {(195, 291), (295, 391)}
	// go through pages of ext_candidate_paths
	for(int i = 0; i < ext_candidate_paths_10.size(); i++)
	{	
		// allocate a 2d memory(page) for current page in the ext_candidate_paths and add it to ext_candidate_LPs
		vector<vector<tuple<int, int> > > temp_vector1;
		ext_candidate_LPs_10.push_back(temp_vector1);

		// go through the paths(rows) of the current page
		for( int j =  0 ; j < ext_candidate_paths_10[i].size() ; j++ )
		{	
			bool flag_check = true;
			// allocate a 1d memory(row) for current row to be added to ext_candidate_LPs
			vector<tuple<int, int> > temp_vector2;

			// go through elements of the current row
			for( int k = 0 ; k < ext_candidate_paths_10[i][j].size() - 1 ; k++)
			{
				// extract all lightpaths and add them to the allocated row (temp_vector2)
				// note that each lightpath is represented by a tuple consist of 2 integers
				if(ext_candidate_paths_10[i][j][k] % 100 == 0)
				{
					int start_index = k + 1;
					int x = start_index + 1;
					while(ext_candidate_paths_10[i][j][x] % 100 == 49 || ext_candidate_paths_10[i][j][x] % 100 == 59)
					{
						x++;
					}
					int end_index = x;	
					
					temp_vector2.push_back(make_tuple(ext_candidate_paths_10[i][j][start_index], ext_candidate_paths_10[i][j][end_index]));	
				
				}
				
			}

			// add the filled row to the current page of ext_candidate_LPs
			ext_candidate_LPs_10[i].push_back(temp_vector2);
		}
	}

	for(int i = 0; i < ext_candidate_paths_100.size(); i++)
	{	
		// allocate a 2d memory(page) for current page in the ext_candidate_paths and add it to ext_candidate_LPs
		vector<vector<tuple<int, int> > > temp_vector1;
		ext_candidate_LPs_100.push_back(temp_vector1);

		// go through the paths(rows) of the current page
		for( int j =  0 ; j < ext_candidate_paths_100[i].size() ; j++ )
		{	
			bool flag_check = true;
			// allocate a 1d memory(row) for current row to be added to ext_candidate_LPs
			vector<tuple<int, int> > temp_vector2;

			// go through elements of the current row
			for( int k = 0 ; k < ext_candidate_paths_100[i][j].size() - 1 ; k++)
			{
				// extract all lightpaths and add them to the allocated row (temp_vector2)
				// note that each lightpath is represented by a tuple consist of 2 integers
				if(ext_candidate_paths_100[i][j][k] % 100 == 0)
				{
					int start_index = k + 1;
					int x = start_index + 1;
					while(ext_candidate_paths_100[i][j][x] % 100 == 49 || ext_candidate_paths_100[i][j][x] % 100 == 59)
					{
						x++;
					}
					int end_index = x;	
					
					temp_vector2.push_back(make_tuple(ext_candidate_paths_100[i][j][start_index], ext_candidate_paths_100[i][j][end_index]));	
				
				}
				
			}

			// add the filled row to the current page of ext_candidate_LPs
			ext_candidate_LPs_100[i].push_back(temp_vector2);
		}
	}



	// clear the candidate_paths directory
	if (system("exec rm candidate_paths/*"));
	
	/*
	write all candidate paths and candidate lightpaths in files
	these files will be generated dynamically each time that the software runs
	and they are just for checking the candidate paths so the software do not use these files as inputs
	*/
	for (size_t i = 0 ; i < ext_candidate_paths_10.size() ; i++)
	{
		ofstream PathsFile("candidate_paths/ext_paths" + to_string(i) + "_10.txt");
		PathsFile << "RequestID = " << i << endl;
		PathsFile << "NumberOfPaths = " << ext_candidate_paths_10[i].size() <<endl;
		for (size_t j = 0 ; j < ext_candidate_paths_10[i].size() ; j++)
		{
			for (size_t k = 0 ; k < ext_candidate_paths_10[i][j].size() ; k++)
			{
				PathsFile << ext_candidate_paths_10[i][j][k];
				if (k < ext_candidate_paths_10[i][j].size() - 1)
					PathsFile << ",";
			}
			PathsFile << "\n";	
		}
		PathsFile.close();
	}

	for (size_t i = 0 ; i < ext_candidate_LPs_10.size() ; i++)
	{
		ofstream PathsFile("candidate_paths/ext_paths" + to_string(i) + "_10_LPs.txt");
		PathsFile << "RequestID = " << i << endl;
		PathsFile << "NumberOfPaths = " << ext_candidate_LPs_10[i].size() << endl;
		for (size_t j = 0 ; j < ext_candidate_LPs_10[i].size() ; j++)
		{
			for (size_t k = 0 ; k < ext_candidate_LPs_10[i][j].size() ; k++)
			{
				PathsFile << "(" ;
				PathsFile << get<0>(ext_candidate_LPs_10[i][j][k]);
				PathsFile << ", " ;
				PathsFile << get<1>(ext_candidate_LPs_10[i][j][k]);
				PathsFile << ")" ;
				if (k < ext_candidate_LPs_10[i][j].size() - 1)
					PathsFile << ", ";
			}
			PathsFile << "\n";	
		}
		PathsFile.close();
	}


	for (size_t i = 0 ; i < ext_candidate_paths_100.size() ; i++)
	{
		ofstream PathsFile("candidate_paths/ext_paths" + to_string(i) + "_100.txt");
		PathsFile << "RequestID = " << i << endl;
		PathsFile << "NumberOfPaths = " << ext_candidate_paths_100[i].size() <<endl;
		for (size_t j = 0 ; j < ext_candidate_paths_100[i].size() ; j++)
		{
			for (size_t k = 0 ; k < ext_candidate_paths_100[i][j].size() ; k++)
			{
				PathsFile << ext_candidate_paths_100[i][j][k];
				if (k < ext_candidate_paths_100[i][j].size() - 1)
					PathsFile << ",";
			}
			PathsFile << "\n";	
		}
		PathsFile.close();
	}

	for (size_t i = 0 ; i < ext_candidate_LPs_100.size() ; i++)
	{
		ofstream PathsFile("candidate_paths/ext_paths" + to_string(i) + "_100_LPs.txt");
		PathsFile << "RequestID = " << i << endl;
		PathsFile << "NumberOfPaths = " << ext_candidate_LPs_100[i].size() << endl;
		for (size_t j = 0 ; j < ext_candidate_LPs_100[i].size() ; j++)
		{
			for (size_t k = 0 ; k < ext_candidate_LPs_100[i][j].size() ; k++)
			{
				PathsFile << "(" ;
				PathsFile << get<0>(ext_candidate_LPs_100[i][j][k]);
				PathsFile << ", " ;
				PathsFile << get<1>(ext_candidate_LPs_100[i][j][k]);
				PathsFile << ")" ;
				if (k < ext_candidate_LPs_100[i][j].size() - 1)
					PathsFile << ", ";
			}
			PathsFile << "\n";	
		}
		PathsFile.close();
	}
	
}

int Network::calculateTotalVertices(int node_vertices, vector <Node* > node_list)
{
	// find total graph nodes that we need for generating candidate paths
	// for each network node we need 7 graph nodes
	// vertice 0 -> corresponds to network node
	// vertice 1 -> corresponds to choosing 10G interface left
	// vertice 2 -> corresponds to choosing 10G interface right
	// vertice 3 -> corresponds to choosing tpd card left
	// vertice 4 -> corresponds to choosing tpd card right
	// vertice 5 -> corresponds to choosing roadm left
	// vertice 6 -> corresponds to choosing roadm right
	int nVertices = 0;
	//vector <int > node_ring = ring_type;
	vector<Node*>::const_iterator node_itr;
    for (node_itr = node_list.begin(); node_itr != node_list.end(); node_itr++) 
	{
		if((*node_itr)->getNodeCheck())
		{
			nVertices += node_vertices;
		}   
		else
		{
			nVertices += 2;
		}
	}
	return nVertices;
}

void Network::mapRequestToPair()
{
	// this function finds for each connection request which is the correspondig node pair and we set the index of that node pair
	// for example if the connection request is from 1 to 2 it corresponds to the node pair (1, 2)

	vector<Connection*>::const_iterator request_itr;
	vector<Connection*>::const_iterator node_pair_itr;
	// go through connection requests
    for (request_itr = connection_requests.begin(); request_itr != connection_requests.end(); request_itr++)
	{
		int node_pair_index = 0;
        int connection_src = (*request_itr)->getSrcID() / 100; // get source node of the current connection request
        int connection_dst = (*request_itr)->getDstID() / 100; // get destination node of the current connection request

		// go through node pairs
        for (node_pair_itr = node_pair_requests.begin(); node_pair_itr != node_pair_requests.end(); node_pair_itr++)
		{
            int node_pair_src = (*node_pair_itr)->getSrcID(); // get source id of current node pair
            int node_pair_dst = (*node_pair_itr)->getDstID(); // get destination id of current node pair

			// if the source and the destination of the current connection 
			// is equal to the source and destination of the current node pair
            if (connection_src == node_pair_src && connection_dst == node_pair_dst)
        	{  
				// set the index of current node pair in the current connection
				(*request_itr)->setNodePairIndex(node_pair_index);	
            }
				
			node_pair_index ++;
        }     
    }
}

void Network::runExternalGA()
{
    cout << "---- GA has been started  ----" << endl;
	// allocate memory for chromosome structure
    vector<vector<float>> chromosome_struct_routing;

	// information about groups so that GA can perform mutations in groups
	vector<vector<int> > mutation_modes_matrix;
	vector<vector<int> > important_mutation_modes_matrix = mutation_importance();

	get_baseline_population();


    // there are as many gene-clusters, as many connection requests
    for (int i = 0; i < number_connection_requests; i ++)
    {
		// allocate memory for the current gene-cluster
        vector<float> temp;

		vector<int> mutation_modes;

		// we need to find how many genes the current gene-cluster has
		// there are as many genes, as many candidate paths for the corresponding connection
        int cluster_size = 0;
		// if the connection is not protected
		// use the related page in the ext_candidate_paths
		// (we have already set the related page index for each connection in mapPairToRequest function)
		// but if the connection is protected: (before we have added two connection instances for each protected request)
		// there is one connection instance with protection code = 1 and another one with protection code = 2
		// it does not mean that 1 is primary and 2 is secondary path, they represent two paths which are redundant to each others
		
		if (connection_requests[i]->getCapacity() > float(10))
		{
			cluster_size = ext_candidate_paths_100[connection_requests[i]->getNodePairIndex()].size();
		}

		else
		{
			cluster_size = ext_candidate_paths_10[connection_requests[i]->getNodePairIndex()].size();
		}
		
		// now we have found the cluster size or number of genes in the current cluster
		// so we add 1 element for each gene to the memory
        for (int j = 0; j < cluster_size; j ++)
        {
            temp.push_back(1);
        }
		
		// add the cluster to the choromosome structure
        chromosome_struct_routing.push_back(temp);

		mutation_modes_matrix.push_back(mutation_modes);
    }

	// choose the population size
	int population_size = 800;

	if (number_nodes == 5)
	{
		//population_size = 1200;
	}
	else if (number_nodes == 6)
	{
		//population_size = 1200;
	}

	// all connections need to be routed
	bool every_gene_must_be_chosen = true;

	// if it is true GA runs with the fast run mode
	bool fast_run = false;

	// if true GA shows a status line in the terminal
	bool print_status_terminal = true;

	// create an instance of class GeneticAlgorithm
	GeneticAlgorithm GA_routing(population_size, chromosome_struct_routing, mutation_modes_matrix, important_mutation_modes_matrix,
				 GeneticAlgorithm :: NB_placement, every_gene_must_be_chosen, fast_run, print_status_terminal, max_number_generation);

	// get the initialization vector, it contains some solutions that GA can start with (to be used in the first generation)
	// it does not need to contain as many solutions as the population size
	// GA will add random solutions to it to reach the population size
	// more detail on the initialization vector is availabe in the GA_initializer function
	vector<vector<int> > GA_initializer_vector;// = GA_initializer(population_size);
	vector<vector< int >> temp_initialize;
	// for (int i = 0; i < population_size; i++)
	// {
	// 	temp_initialize.push_back({0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0});
	
	// }
	// GA_initializer_vector = temp_initialize;

	// create the first generation of the population
	bool use_the_init_vector = false;
	GA_routing.first_generation(use_the_init_vector, GA_initializer_vector);

	// main loop, it runs until GA reaches the stopping condition
	while(true)
	{
		// allocate memory for saving the feasibility and fitness values of the entire population
        vector<float> feasibility_vect(population_size);
        vector<float> fitness_value_vect(population_size);

        // check every solution in the population
        for (int R_solution_ind = 0; R_solution_ind < population_size; R_solution_ind ++)
        {
			// allocate memory for saving which candidates are chosen by the current solution
            vector<int> candidate_choices;

			// go through the gene clusters (correspond to connection requests)
            for(int gene_cluster_ind = 0; gene_cluster_ind < number_connection_requests; gene_cluster_ind ++)
            {
                // find out which candidate was chosen for this request
                int candidate_id = (int)(GA_routing.get_selected_gene(R_solution_ind, gene_cluster_ind));
				// save the chosen candidate
                candidate_choices.push_back(candidate_id);
            }			

			// now we have the index of selected candidates
			// we need to find the acutal path and lightpaths correspond to each index
			// and save them in the connection requests
			// more details is available in the set_selected_paths function
			set_selected_paths(candidate_choices);

			if (ari_debug)
			{
				for (int i = 0; i < connection_requests.size(); i++)
				{
					cout << "connection " << i; 
					cout << " from " << connection_requests[i]->getSrcID();
					cout << " to " << connection_requests[i]->getDstID();
					cout << " capacity " << connection_requests[i]->getCapacity() << endl;
					vector<int> path_print = connection_requests[i]->getMainPath();
					for (int j = 0; j < path_print.size(); j++)
					{
						cout << path_print[j] << " ";
					}
					cout << endl << endl;
				}
			}
			// find feasibility and fitness value for the current solution
			float feasibility = 0;  
            float fitness_value = 0;
			tuple<float, float> feasibility_fitness;
			feasibility_fitness = calculate_feasibility_fitness();
			feasibility = get<0>(feasibility_fitness);
			fitness_value = get<1>(feasibility_fitness);

			if (ari_debug)
			{
				cout << "feasibility " << feasibility << endl;
				cout << "fitness " << fitness_value << endl;

				cin.ignore();
			}
			

			// save the values
			feasibility_vect[R_solution_ind] = feasibility;
            fitness_value_vect[R_solution_ind] = fitness_value;
		}
		// GA needs a 2d matrix for the fitness values, for each solution in every population
		// so we save all the fitness values 
		// but the feasibility is only needed for each solution in the current population 
        vector<vector<float>> fitness_matrix;
        fitness_matrix.push_back(fitness_value_vect);

		// build the next generation according to the feasibilities and fitness values    
        GA_routing.next_generation(feasibility_vect, fitness_matrix);
		
		// if stopping condition has been reached
        if (GA_routing.is_improved() == false)
        {
			cout << "---- GA has been finished ----                                                     " << endl;
			cout << "preparing the results ..." << endl;

            // now population only contains best solutions that GA could find
			// we can access them via GA_routing.get_selected_gene(), as above
			// note that all the solutions in this last population are not the exact optimum one
			// so it contains solutions with the best cost as well as some solutions close to that cost
			// when we set the last population it returns the new population size because the last population
			// does not contain as many solutions as the previous populations (initial population size defined above)
			population_size = GA_routing.set_best_solutions();

			// break from the infinite loop
            break;      
        }
	}

	// now we have the last population and we need to check all solutions in it
	// exactly like above but here we are not in an infinite loop
	// so check all the solutions and find which one is the best
	// the procedure is as same as above
	float best_cost = 1e6;
	int best_solution_index = -1;
	// check every solution in the last population , note that the population size has been updated
	for (int R_solution_ind = 0; R_solution_ind < population_size; R_solution_ind ++)
	{
		// allocate memory for saving which candidates are chosen by the current solution
		vector<int> candidate_choices;

		// go through the gene clusters (correspond to connection requests)
		for(int gene_cluster_ind = 0; gene_cluster_ind < number_connection_requests; gene_cluster_ind ++)
		{
			// find out which candidate was chosen for this request
			int candidate_id = (int)(GA_routing.get_selected_gene(R_solution_ind, gene_cluster_ind));
			// save the chosen candidate
			candidate_choices.push_back(candidate_id);
		}

		// find and set the selected paths
		set_selected_paths(candidate_choices);

		// calculate feasibility and fitness value
		float feasibility = 0;  
		float fitness_value = 0;
		tuple<float, float> feasibility_fitness;
		feasibility_fitness = calculate_feasibility_fitness();
		feasibility = get<0>(feasibility_fitness);
		fitness_value = get<1>(feasibility_fitness);

		// find if it the best
		if (feasibility == 1 && fitness_value < best_cost)
		{
			best_cost = fitness_value;
			best_solution_index = R_solution_ind;
		}
	}

	// now we know which solution in the last population is the best one (best_solution_index)
	// so we do the exact procedure for this solution again and prepare the results
	// we could save the values calculated above so we don't need to calculate it again for the best one
	// but doing it separately allows us to prepare additional results for printing and prepare the result file

	// allocate memory for saving which candidates are chosen by the current solution
	vector<int> candidate_choices;

	// go through the gene clusters (correspond to connection requests)
	for(int gene_ind = 0; gene_ind < number_connection_requests; gene_ind ++)
	{
		// find out which candidate was chosen in the best solution for this request
		int candidate_id = (int)(GA_routing.get_selected_gene(best_solution_index, gene_ind));
		// save the chosen candidate
		candidate_choices.push_back(candidate_id);
	}

	
	vector<vector<int>> selected_paths;
	set_selected_paths(candidate_choices);
	

	// calculate feasibility and fitness value
	float feasibility = 0;  
	float fitness_value = 0;
	tuple<float, float> feasibility_fitness;
	// here we pass the true argument to the function in order to let it prepare the results
	feasibility_fitness = calculate_feasibility_fitness(true);
	feasibility = get<0>(feasibility_fitness);
	fitness_value = get<1>(feasibility_fitness);

	cout << "final best feasibility:   " << feasibility << endl;
	cout << "final best fitness:   " << fitness_value << endl;
	for (int i = 0; i < candidate_choices.size(); i++)
	{
		cout << candidate_choices[i] <<", ";
	}
}

void Network::set_selected_paths (vector<int> selected_candidates)
{	
	/*
	this function gets a 1d vector containing selected candidates by the GA
	it explores the vector and finds the corresponding path and lightpath from the calculated paths and lightpaths
	and sets them to the related connection request
	*/

	// go through the selected_candidates
	// note that the variable i represents not only the index in the selected_candidates vector
	// but also the index of corresponding connection request, because the selected_candidates vector filled up 
	// with the same order that the connection_requests vector is filled
	for (int i = 0; i < selected_candidates.size(); i++)
	{
		// get the index of node pair related to this connection request
		int nodepair_index = connection_requests[i]->getNodePairIndex();

		// extract the index of the selected candidate
		int selected_candidate = selected_candidates[i];

		// find and set the path and lightpaths
		// according to protection id, choose to use one of the three
		// ext_candidate_paths, ext_candidate_paths_protected1 or ext_candidate_paths_protected2 

		if (connection_requests[i]->getCapacity() > float(10))
		{
			connection_requests[i]->setMainPath(ext_candidate_paths_100[nodepair_index][selected_candidate]);
			connection_requests[i]->setMainLPs(ext_candidate_LPs_100[nodepair_index][selected_candidate]);
		}
		else
		{
			connection_requests[i]->setMainPath(ext_candidate_paths_10[nodepair_index][selected_candidate]);
			connection_requests[i]->setMainLPs(ext_candidate_LPs_10[nodepair_index][selected_candidate]);
		}

	}
}

tuple<float, float> Network::calculate_feasibility_fitness(bool print_results)
{

	float feasibility = 0;
	float fitness = 0;
	int number_TPD_right = 40;
	int number_TPD_left = 40;
	int total_number_TPD = number_TPD_right + number_TPD_left;
	int number_OTU2_right = 10;
	int number_OTU2_left = 10;
	int total_number_OTU2 = number_OTU2_right + number_OTU2_left;
	int total_colored_interfaces = total_number_TPD + (total_number_OTU2 * 4);
	int actual_interfaces[total_colored_interfaces];
	for (int i = 0; i < number_TPD_left; i++)
	{
		actual_interfaces[i] = 100 + i;
	}
	for (int i = 0; i < number_TPD_right; i++)
	{
		actual_interfaces[number_TPD_left + i] = 200 + i;
	}
	for (int i = 0; i < number_OTU2_left * 4; i++)
	{
		actual_interfaces[total_number_TPD + i] = 300 + i;
	}
	for (int i = 0; i < number_OTU2_right * 4; i++)
	{
		actual_interfaces[total_number_TPD +  (number_OTU2_left * 4) + i] = 400 + i;
	}

	//int actual_interfaces[12] = {47,11,48,12,91,92,93,94,95,96,97,98};
	//int actual_interfaces[66] = {47,81,82,83,84,48,85,86,87,88,91,92,93,94,71,72,73,74,61,62,63,64,51,52,53,54,31,32,33,34,30,50,60,70,41,42,43,44,95,96,97,98,75,76,77,78,65,66,67,68,55,56,57,58,35,36,37,38,39,40,69,79,45,46,90,99};

	float used_capacity[number_nodes][total_colored_interfaces];
	int other_end_inds[number_nodes][total_colored_interfaces];	
	bool is_used[number_nodes][total_colored_interfaces];

	bool drop_add[number_nodes][total_colored_interfaces];
	float drop_add_capacity[number_nodes][total_colored_interfaces];

	int tpd_access_ports_needed[number_nodes][total_number_TPD];
	int otu4_access_ports_needed[number_nodes][total_number_TPD];

	int otu2_access_ports_needed[number_nodes][total_number_OTU2];


	for (int i = 0; i < number_nodes; i++)
	{
		for (int j = 0; j < total_colored_interfaces; j++)
		{
			used_capacity[i][j] = 0.0;
			other_end_inds[i][j] = 0;
			is_used[i][j] = false;
			drop_add[i][j] = false;
			drop_add_capacity[i][j] = 0.0;
		}

		for (int j = 0; j < total_number_TPD; j++)
		{
			tpd_access_ports_needed[i][j] = 0;
			otu4_access_ports_needed[i][j] = 0;
		}

		for (int j = 0; j < total_number_OTU2; j++)
		{
			otu2_access_ports_needed[i][j] = 0;
		}
	}

	bool is_connections_routed[number_connection_requests];	
	for (int j = 0; j < number_connection_requests; j++)
	{
		is_connections_routed[j] = false;
	}

	vector<Lightpath*> total_lps;
	
	// go through the connection requests
	for (int i = 0; i < number_connection_requests; i++)
	{
		// get the capacity needed by this connection
		float connection_capacity = connection_requests[i]->getCapacity();

		// get the lightpaths which are needed for routing this connection
		vector<tuple<int, int> > LPs_vector = connection_requests[i]->getMainLPs();

		vector<int> main_path = connection_requests[i]->getMainPath();

		vector<tuple<int, int> > actual_LPs_vector;

		// define an array to keep track of routing into each lightpath
		bool is_routed[LPs_vector.size()] = {false};

		int client_actual_interface1 = 0;
		int client_actual_interface2 = 0;

		// go through all lightpaths which are needed for this connection to be routed
		for (int k = 0; k < LPs_vector.size(); k++)
		{
			
			// get the information of the end-points of the current lightpath
			int LP_endpoint1 = get<0> (LPs_vector[k]);
			int LP_endpoint2 = get<1> (LPs_vector[k]);
			int node_id_endpoint1 = LP_endpoint1 / 100;
			int node_id_endpoint2 = LP_endpoint2 / 100;
			int interface_id_endpoint1 = LP_endpoint1 % 100;
			int interface_id_endpoint2 = LP_endpoint2 % 100; 
			

			// set the parameters related to the end-point1 of the current lightpath according to the type of interface
			int interface_ind_start1 = 0;
			int interface_ind_end1 = 0;
			float capacity1 = 0;			
			bool is_routed_endpoint1 = false;
			int roadm_id1 = 0;
			int lp_type = 0;
			switch (interface_id_endpoint1)
			{
				case 47: // if it is tpd card left
				{
					capacity1 = float(200);
					interface_ind_start1 = 0;
					interface_ind_end1 = number_TPD_left;
					roadm_id1 = 49;
					lp_type = 100;
					break;
				}

				case 48: // if it is tpd card right
				{
					capacity1 = float(200);
					interface_ind_start1 = number_TPD_left;
					interface_ind_end1 = total_number_TPD;
					roadm_id1 = 59;
					lp_type = 100;
					break;
				}

				case 91: // if it is tpd card right
				{
					capacity1 = float(10);
					interface_ind_start1 = total_number_TPD;
					interface_ind_end1 = total_number_TPD + (number_OTU2_left * 4);
					roadm_id1 = 49;
					lp_type = 10;
					break;
				}

				case 95: // if it is tpd card right
				{
					capacity1 = float(10);
					interface_ind_start1 = total_number_TPD + (number_OTU2_left * 4);
					interface_ind_end1 = total_number_TPD + (total_number_OTU2 * 4);
					roadm_id1 = 59;
					lp_type = 10;
					break;
				}

			}

			// set the parameters related to the end-point1 of the current lightpath according to the type of interface
			int interface_ind_start2 = 0;
			int interface_ind_end2 = 0;
			float capacity2 = 0;
			int roadm_id2 = 0;
			bool is_routed_endpoint2 = false;
			switch (interface_id_endpoint2)
			{
				case 47: // if it is tpd card left
				{
					capacity2 = float(200);
					interface_ind_start2 = 0;
					interface_ind_end2 = number_TPD_left;
					roadm_id2 = 49;
					lp_type = 100;
					break;
				}

				case 48: // if it is tpd card right
				{
					capacity2 = float(200);
					interface_ind_start2 = number_TPD_left;
					interface_ind_end2 = total_number_TPD;
					roadm_id2 = 59;
					lp_type = 100;
					break;
				}

				case 91: // if it is tpd card right
				{
					capacity2 = float(10);
					interface_ind_start2 = total_number_TPD;
					interface_ind_end2 = total_number_TPD + (number_OTU2_left * 4);
					roadm_id2 = 49;
					lp_type = 10;
					break;
				}

				case 95: // if it is tpd card right
				{
					capacity2 = float(10);
					interface_ind_start2 = total_number_TPD + (number_OTU2_left * 4);
					interface_ind_end2 = total_number_TPD + (total_number_OTU2 * 4);
					roadm_id2 = 59;
					lp_type = 10;
					break;
				}

			}

			int actual_interface1;
			int actual_interface2;

			// go through existing interfaces for the end-point1
			for (int interface_ind = interface_ind_start1; interface_ind < interface_ind_end1; interface_ind++)
			{
				// do the routing and assign interface only if it (endpoint1) has not been routed yet
				if (is_routed_endpoint1 == false)
				{
					// if current interface is already used (lightpath is established on this interface)
					if (is_used[node_id_endpoint1 - 1][interface_ind] == true)
					{
						// check if the interface has capacity to carry the connection (possibility of grooming in term of capacity)
						if (used_capacity[node_id_endpoint1 - 1][interface_ind] + connection_capacity <= capacity1)
						{
							// check if the interface (lightpath) has the same other-end as the connection needs
							// (possibility of grooming in term of lightpath establishment)
							if (other_end_inds[node_id_endpoint1 - 1][interface_ind] == LP_endpoint2)
							{
								// if both conditions are met we can groom the connection in this existing lightpath
								// so no need for new lightpath to be established

								// add the used capacity 
								used_capacity[node_id_endpoint1 - 1][interface_ind] += connection_capacity;

								// save that our connection has been routed successfully in the first end-point interface (lightpath)
								is_routed_endpoint1 = true;

								actual_interface1 = (node_id_endpoint1 * 1000) + actual_interfaces[interface_ind];
						
								if (k == 0)
								{
									client_actual_interface1 = actual_interface1;
								}
								
							}
						}
					}
					// otherwise we need to establish a new lightpath on this interface
					else
					{
						// check if the interface has capacity to carry the connection (possibility of grooming in term of capacity)
						if (used_capacity[node_id_endpoint1 - 1][interface_ind] + connection_capacity <= capacity1)
						{
							// save status of the interface showing that it is used and there is a lightpath established on it
							is_used[node_id_endpoint1 - 1][interface_ind] = true;

							// add the used capacity
							used_capacity[node_id_endpoint1 - 1][interface_ind] += connection_capacity;

							// save the other endpoint of the lightpath 
							// (we need to know this because for other connections we want to check the possibility of grooming)
							other_end_inds[node_id_endpoint1 - 1][interface_ind] = LP_endpoint2;

							// save that our connection has been routed successfully in the first end-point interface
							is_routed_endpoint1 = true;

							actual_interface1 = (node_id_endpoint1 * 1000) + actual_interfaces[interface_ind];

							if (k == 0)
							{
								client_actual_interface1 = actual_interface1;
							}
						}
					}
				}
			}

			// go through existing interfaces for the end-point2
			for (int interface_ind = interface_ind_start2; interface_ind < interface_ind_end2; interface_ind++)
			{
				// do the routing and assign interface only if it (endpoint2) has not been routed yet
				if (is_routed_endpoint2 == false)
				{
					// if current interface is already used (lightpath is established on this interface)
					if (is_used[node_id_endpoint2 - 1][interface_ind] == true)
					{
						// check if the interface has capacity to carry the connection (possibility of grooming in term of capacity)
						if (used_capacity[node_id_endpoint2 - 1][interface_ind] + connection_capacity <= capacity2)
						{
							// check if the interface (lightpath) has the same other-end as the connection needs
							// (possibility of grooming in term of lightpath establishment)
							if (other_end_inds[node_id_endpoint2 - 1][interface_ind] == LP_endpoint1)
							{
								// if both conditions are met we can groom the connection in this existing lightpath
								// so no need for new lightpath to be established

								// add the used capacity 
								used_capacity[node_id_endpoint2 - 1][interface_ind] += connection_capacity;

								// save that our connection has been routed successfully in the second end-point interface (lightpath)
								is_routed_endpoint2 = true;

								
								actual_interface2 = (node_id_endpoint2 * 1000) + actual_interfaces[interface_ind];

								if (k == LPs_vector.size() - 1)
								{
									client_actual_interface2 = actual_interface2;
								}
							}
						}
					}
					// otherwise we need to establish a new lightpath on this interface
					else
					{
						// check if the interface has capacity to carry the connection (possibility of grooming in term of capacity)
						if (used_capacity[node_id_endpoint2 - 1][interface_ind] + connection_capacity <= capacity2)
						{
							// save status of the interface showing that it is used and there is a lightpath established on it
							is_used[node_id_endpoint2 - 1][interface_ind] = true;

							// add the used capacity
							used_capacity[node_id_endpoint2 - 1][interface_ind] += connection_capacity;

							// save the other endpoint of the lightpath 
							// (we need to know this because for other connections we want to check the possibility of grooming)
							other_end_inds[node_id_endpoint2 - 1][interface_ind] = LP_endpoint1;

							// save that our connection has been routed successfully in the first end-point interface
							is_routed_endpoint2 = true;


							actual_interface2 = (node_id_endpoint2 * 1000) + actual_interfaces[interface_ind];

							if (k == LPs_vector.size() - 1)
							{
								client_actual_interface2 = actual_interface2;
							}
						}
					}
				}
			}
			actual_LPs_vector.push_back(make_tuple(actual_interface1, actual_interface2));
			// check if the connection could be routed on both end-points of the current lightpath
			// either groomed wih other connections or routed on a new established lightpath
			if (is_routed_endpoint1 && is_routed_endpoint2)
			{
				

				// save that the connection is routed on the current lightpath(k)
				is_routed[k] = true;

				// preparing list of lightpaths for printing and saving the results
				if (print_results || true)
				{
					vector<Lightpath*>::const_iterator lp_itr;
					bool found_lp = false;
					for (lp_itr = total_lps.begin(); lp_itr != total_lps.end(); lp_itr++) 
					{
						if ((*lp_itr)->getEndId1() == actual_interface1 && (*lp_itr)->getEndId2() == actual_interface2)
						{
							found_lp = true;
							(*lp_itr)->insert_connection(i);
							(*lp_itr)->add_used_capacity(connection_capacity);
							break;
						}
						if ((*lp_itr)->getEndId1() == actual_interface2 && (*lp_itr)->getEndId2() == actual_interface1)
						{
							found_lp = true;
							(*lp_itr)->insert_connection(i);
							(*lp_itr)->add_used_capacity(connection_capacity);
							break;
						}
					}
					if (found_lp == false)
					{
						vector <Unifiber*> usedFibersinLightpath;
						vector<Unifiber*>::const_iterator fiber_itr;
						int x = 0, y = 0;
						for (int i = 0; i < main_path.size() - 1; i++)
						{
							bool flag = false;
							if (main_path[i] % 100 == 59 && main_path[i + 1] % 100 == 49)
							{
								x = main_path[i];
								y = main_path[i + 1];
								flag = true;
							}
							else if (main_path[i] % 100 == 49 && main_path[i + 1] % 100 == 59)
							{
								x = main_path[i];
								y = main_path[i + 1];
								flag = true;
							}
							else if (main_path[i] % 100 == 49 && main_path[i + 1] % 100 == 49)
							{
								x = main_path[i];
								y = main_path[i + 1];
								flag = true;
							}
							else if (main_path[i] % 100 == 59 && main_path[i + 1] % 100 == 59)
							{
								x = main_path[i];
								y = main_path[i + 1];
								flag = true;
							}
							
							if (flag == true)
							{
								for (fiber_itr = uni_fibers.begin(); fiber_itr != uni_fibers.end(); fiber_itr++) 
								{
									if (x == (*fiber_itr)-> getSrcId() && y == (*fiber_itr)-> getDstId())
									{
										usedFibersinLightpath.push_back(*fiber_itr);
									}
								}	
							}
						}

						total_lps.push_back(new Lightpath(actual_interface1, actual_interface2, lp_type, usedFibersinLightpath));
						total_lps[total_lps.size() - 1]->insert_connection(i);
						total_lps[total_lps.size() - 1]->add_used_capacity(connection_capacity);
					}
				}
			}
		}

		// check and save if the connection is routed properly or not
		// we need to check the routing status of the connection in each lightpath
		// the connection is considered routed only if it could be routed into all lightpaths
		/* Example:
		assume we have a connection request from node1 to node5 and the selected path by GA is:
		"100,195,159,249,291,200,295,259,349,391,300,395,359,449,491,400,495,459,549,591,500"
		the corresponding lightpaths which are needed to be established are: 
		(195, 291), (295, 391), (395, 491), (495, 591)
		so for routing the connection into this path we need to be able to route it into all of these lightpaths
		and if for instance we could not to route it into (395, 491), it means that the connection is not routed
		*/

		bool is_connection_routed = true;
		for (int j = 0; j < LPs_vector.size(); j++)
		{
			if (is_routed[j] == false)
			{
				is_connection_routed = false;
				break;
			}
		}
		

		is_connections_routed[i] = is_connection_routed;

		
		
		for (int j = 0; j < actual_LPs_vector.size() - 1; j++)
		{
			int current_LP_endpoint2 = get<1> (actual_LPs_vector[j]);
			int current_LP_interface_id_endpoint2 = current_LP_endpoint2 % 1000;
			int current_LP_Node = current_LP_endpoint2 / 1000;
			int next_LP_endpoint1 = get<0> (actual_LPs_vector[j + 1]);
			int next_LP_interface_id_endpoint1 = next_LP_endpoint1 % 1000;
			int next_LP_Node = next_LP_endpoint1 / 1000; 
			 

			for (int index = 0; index < total_colored_interfaces; index ++)
			{
				if (actual_interfaces[index] == current_LP_interface_id_endpoint2)
				{
					drop_add[current_LP_Node - 1][index] = true;
					drop_add_capacity[current_LP_Node - 1][index] += connection_capacity;
					break;
				}

				else if (actual_interfaces[index] == next_LP_interface_id_endpoint1)
				{
					drop_add[next_LP_Node - 1][index] = true;
					drop_add_capacity[next_LP_Node - 1][index] += connection_capacity;
					break;
				}
			}



		}
		// get the source node id and destination node id of the current connection request
		int connection_src_node = client_actual_interface1 / 1000;
		int connection_dst_node = client_actual_interface2 / 1000;

		// get the source interface id and destination interface id of the selected path for the current connection request
		int connection_src_interface = client_actual_interface1 % 1000;
		int connection_dst_interface = client_actual_interface2 % 1000;

		for (int index = 0; index < total_number_TPD; index ++)
		{
			if (actual_interfaces[index] == connection_src_interface)
			{
				if (connection_capacity > 10)
				{
					tpd_access_ports_needed[connection_src_node - 1][index] ++;
				}
				else if (connection_capacity <= 10)
				{
					otu4_access_ports_needed[connection_src_node - 1][index] ++;
				}
			}
		}
		for (int index = 0; index < total_number_TPD; index ++)
		{

			if (actual_interfaces[index] == connection_dst_interface)
			{
				if (connection_capacity > 10)
				{
					tpd_access_ports_needed[connection_dst_node - 1][index] ++;
				}
				else if (connection_capacity <= 10)
				{
					otu4_access_ports_needed[connection_dst_node - 1][index] ++;
				}
			}
		}

		for (int index = 0; index < total_number_OTU2; index ++)
		{
			for (int int_index = 0; int_index < 4; int_index ++)
			{
				if (actual_interfaces[total_number_TPD + (index * 4) + int_index] == connection_src_interface)
				{
					otu2_access_ports_needed[connection_src_node - 1][index] ++;
					//break;
				}

				if (actual_interfaces[total_number_TPD + (index * 4) + int_index] == connection_dst_interface)
				{
					otu2_access_ports_needed[connection_dst_node - 1][index] ++;
					//break;
				}
			}
		}	
	}


	baseline_run ++;

	vector<Lightpath*>::const_iterator lp_itr;
	vector<Unifiber*>::reverse_iterator fiber_itr;
	vector<Unifiber*>::const_iterator fiber_itr1;
	vector<Lightpath*> total_full_lps;
	for (lp_itr = total_lps.begin(); lp_itr != total_lps.end(); lp_itr++) 
	{
		total_full_lps.push_back((*lp_itr));

		vector<Unifiber*> opposite_fiber;
		for (fiber_itr = (*lp_itr)->fibers.rbegin(); fiber_itr != (*lp_itr)->fibers.rend(); fiber_itr++) 
		{	
			for (fiber_itr1 = uni_fibers.begin(); fiber_itr1 != uni_fibers.end(); fiber_itr1++) 
			{	
				if ((*fiber_itr)->getSrcId() == (*fiber_itr1)->getDstId() && (*fiber_itr)->getDstId() == (*fiber_itr1)->getSrcId())
				{
					opposite_fiber.push_back((*fiber_itr1));
				}

			}
		}
		
		total_full_lps.push_back(new Lightpath((*lp_itr)->getEndId2(), (*lp_itr)->getEndId1(), (*lp_itr)->getType(), opposite_fiber));	
		total_full_lps[total_full_lps.size() - 1]->routed_connections = (*lp_itr)->routed_connections;
		total_full_lps[total_full_lps.size() - 1]->add_used_capacity((*lp_itr)->capacity_used);
	}

	total_lps = total_full_lps;

	final_lps = total_lps;
	//float oa_feasibility = oa_baseline_mode(total_lps);
	vector<bool> unfeasible_check = oa_baseline_mode(total_lps);

	// define two variables for calculating the feasibility of the solution
	// for every constraint we increment the total_score so at the end we know how many checks we have done
	// but we increment the score only if the constraint is passed 
	// at the end the feasibility will be the score / total_score
	float score = 0;  
	float total_score = 0;
	bool all_LPs_OA_feasible = true;
	for(int i = 0 ; i < unfeasible_check.size(); i++)
	{
		if (unfeasible_check[i] == false)
		{
			all_LPs_OA_feasible = false;
			break;
		}
	}
	
	// if (all_LPs_OA_feasible == false)
	// {
	// 	total_score += 1;
	// }
	// // *************************************************************************
	// // ******************************* THIS IS A 100G check for grooming **************************
	if (all_LPs_OA_feasible == false)
	{
		vector <bool> connection_100_200;
		for (int i = 0; i < number_connection_requests; i++)
		{
			for (int j = 0; j < total_lps.size(); j++) 
			{
				if(find(total_lps[j]->routed_connections.begin(), total_lps[j]->routed_connections.end(), i) != total_lps[j]->routed_connections.end())
				{
					
					connection_100_200.push_back(unfeasible_check[j]);
					break;
				}
			}
		}
		//cout << connection_100_200.size()<<endl;
		feasibility = 0;
		fitness = 0;
		for (int i=0; i < number_nodes; i++)
		{
			for (int j=0; j < total_colored_interfaces; j++)
			{
				used_capacity[i][j] = 0;
				other_end_inds[i][j] = 0;	
				is_used[i][j] = false;
				drop_add[i][j] = false;
				drop_add_capacity[i][j] = 0;
			}
			for (int j=0; j < total_number_TPD; j++)
			{
				tpd_access_ports_needed[i][j] = 0;
				otu4_access_ports_needed[i][j] = 0;
			}
			for (int j=0; j < total_number_OTU2; j++)
			{
				otu2_access_ports_needed[i][j] = 0;
			}
		}
		for (int i=0; i < number_connection_requests; i++)
		{
			is_connections_routed[i] = false;
		}
		
		total_lps.clear();
		
		// go through the connection requests
		for (int i = 0; i < number_connection_requests; i++)
		{
			// get the capacity needed by this connection
			float connection_capacity = connection_requests[i]->getCapacity();

			// get the lightpaths which are needed for routing this connection
			vector<tuple<int, int> > LPs_vector = connection_requests[i]->getMainLPs();
			
			vector<int> main_path = connection_requests[i]->getMainPath();

			vector<tuple<int, int> > actual_LPs_vector;

			// define an array to keep track of routing into each lightpath
			bool is_routed[LPs_vector.size()] = {false};

			int client_actual_interface1 = 0;
			int client_actual_interface2 = 0;

			// go through all lightpaths which are needed for this connection to be routed
			for (int k = 0; k < LPs_vector.size(); k++)
			{
				
				// get the information of the end-points of the current lightpath
				int LP_endpoint1 = get<0> (LPs_vector[k]);
				int LP_endpoint2 = get<1> (LPs_vector[k]);
				int node_id_endpoint1 = LP_endpoint1 / 100;
				int node_id_endpoint2 = LP_endpoint2 / 100;
				int interface_id_endpoint1 = LP_endpoint1 % 100;
				int interface_id_endpoint2 = LP_endpoint2 % 100; 
				

				// set the parameters related to the end-point1 of the current lightpath according to the type of interface
				int interface_ind_start1 = 0;
				int interface_ind_end1 = 0;
				float capacity1 = 0;			
				bool is_routed_endpoint1 = false;
				int roadm_id1 = 0;
				int lp_type = 0;
				switch (interface_id_endpoint1)
				{
					case 47: // if it is tpd card left
					{
						if (connection_100_200[i] == false)
						{
							capacity1 = float(100);
						}
						else
						{
							capacity1 = float(200);
						}
						interface_ind_start1 = 0;
						interface_ind_end1 = number_TPD_left;
						roadm_id1 = 49;
						lp_type = 100;
						break;
					}

					case 48: // if it is tpd card right
					{
						if (connection_100_200[i] == false)
						{
							capacity1 = float(100);
						}
						else
						{
							capacity1 = float(200);
						}
						interface_ind_start1 = number_TPD_left;
						interface_ind_end1 = total_number_TPD;
						roadm_id1 = 59;
						lp_type = 100;
						break;
					}

					case 91: // if it is tpd card right
					{
						capacity1 = float(10);
						interface_ind_start1 = total_number_TPD;
						interface_ind_end1 = total_number_TPD + (number_OTU2_left * 4);
						roadm_id1 = 49;
						lp_type = 10;
						break;
					}

					case 95: // if it is tpd card right
					{
						capacity1 = float(10);
						interface_ind_start1 = total_number_TPD + (number_OTU2_left * 4);
						interface_ind_end1 = total_number_TPD + (total_number_OTU2 * 4);
						roadm_id1 = 59;
						lp_type = 10;
						break;
					}

				}

				// set the parameters related to the end-point1 of the current lightpath according to the type of interface
				int interface_ind_start2 = 0;
				int interface_ind_end2 = 0;
				float capacity2 = 0;
				int roadm_id2 = 0;
				bool is_routed_endpoint2 = false;
				switch (interface_id_endpoint2)
				{
					case 47: // if it is tpd card left
					{
						if (connection_100_200[i] == false)
						{
							capacity2 = float(100);
						}
						else
						{
							capacity2 = float(200);
						}
						interface_ind_start2 = 0;
						interface_ind_end2 = number_TPD_left;
						roadm_id2 = 49;
						lp_type = 100;
						break;
					}

					case 48: // if it is tpd card right
					{
						if (connection_100_200[i] == false)
						{
							capacity2 = float(100);
						}
						else
						{
							capacity2 = float(200);
						}
						interface_ind_start2 = number_TPD_left;
						interface_ind_end2 = total_number_TPD;
						roadm_id2 = 59;
						lp_type = 100;
						break;
					}

					case 91: // if it is tpd card right
					{
						capacity2 = float(10);
						interface_ind_start2 = total_number_TPD;
						interface_ind_end2 = total_number_TPD + (number_OTU2_left * 4);
						roadm_id2 = 49;
						lp_type = 10;
						break;
					}

					case 95: // if it is tpd card right
					{
						capacity2 = float(10);
						interface_ind_start2 = total_number_TPD + (number_OTU2_left * 4);
						interface_ind_end2 = total_number_TPD + (total_number_OTU2 * 4);
						roadm_id2 = 59;
						lp_type = 10;
						break;
					}

				}

				int actual_interface1;
				int actual_interface2;

				
				// go through existing interfaces for the end-point1
				for (int interface_ind = interface_ind_start1; interface_ind < interface_ind_end1; interface_ind++)
				{
					// do the routing and assign interface only if it (endpoint1) has not been routed yet
					if (is_routed_endpoint1 == false)
					{
						// if current interface is already used (lightpath is established on this interface)
						if (is_used[node_id_endpoint1 - 1][interface_ind] == true)
						{
							// check if the interface has capacity to carry the connection (possibility of grooming in term of capacity)
							if (used_capacity[node_id_endpoint1 - 1][interface_ind] + connection_capacity <= capacity1)
							{
								// check if the interface (lightpath) has the same other-end as the connection needs
								// (possibility of grooming in term of lightpath establishment)
								if (other_end_inds[node_id_endpoint1 - 1][interface_ind] == LP_endpoint2)
								{
									// if both conditions are met we can groom the connection in this existing lightpath
									// so no need for new lightpath to be established

									// add the used capacity 
									used_capacity[node_id_endpoint1 - 1][interface_ind] += connection_capacity;

									// save that our connection has been routed successfully in the first end-point interface (lightpath)
									is_routed_endpoint1 = true;

									actual_interface1 = (node_id_endpoint1 * 1000) + actual_interfaces[interface_ind];
							
									if (k == 0)
									{
										client_actual_interface1 = actual_interface1;
									}
									
								}
							}
						}
						// otherwise we need to establish a new lightpath on this interface
						else
						{
							// check if the interface has capacity to carry the connection (possibility of grooming in term of capacity)
							if (used_capacity[node_id_endpoint1 - 1][interface_ind] + connection_capacity <= capacity1)
							{
								// save status of the interface showing that it is used and there is a lightpath established on it
								is_used[node_id_endpoint1 - 1][interface_ind] = true;

								// add the used capacity
								used_capacity[node_id_endpoint1 - 1][interface_ind] += connection_capacity;

								// save the other endpoint of the lightpath 
								// (we need to know this because for other connections we want to check the possibility of grooming)
								other_end_inds[node_id_endpoint1 - 1][interface_ind] = LP_endpoint2;

								// save that our connection has been routed successfully in the first end-point interface
								is_routed_endpoint1 = true;

								actual_interface1 = (node_id_endpoint1 * 1000) + actual_interfaces[interface_ind];

								if (k == 0)
								{
									client_actual_interface1 = actual_interface1;
								}
							}
						}
					}
				}

				// go through existing interfaces for the end-point2
				for (int interface_ind = interface_ind_start2; interface_ind < interface_ind_end2; interface_ind++)
				{
					// do the routing and assign interface only if it (endpoint2) has not been routed yet
					if (is_routed_endpoint2 == false)
					{
						// if current interface is already used (lightpath is established on this interface)
						if (is_used[node_id_endpoint2 - 1][interface_ind] == true)
						{
							// check if the interface has capacity to carry the connection (possibility of grooming in term of capacity)
							if (used_capacity[node_id_endpoint2 - 1][interface_ind] + connection_capacity <= capacity2)
							{
								// check if the interface (lightpath) has the same other-end as the connection needs
								// (possibility of grooming in term of lightpath establishment)
								if (other_end_inds[node_id_endpoint2 - 1][interface_ind] == LP_endpoint1)
								{
									// if both conditions are met we can groom the connection in this existing lightpath
									// so no need for new lightpath to be established

									// add the used capacity 
									used_capacity[node_id_endpoint2 - 1][interface_ind] += connection_capacity;

									// save that our connection has been routed successfully in the second end-point interface (lightpath)
									is_routed_endpoint2 = true;

									
									actual_interface2 = (node_id_endpoint2 * 1000) + actual_interfaces[interface_ind];

									if (k == LPs_vector.size() - 1)
									{
										client_actual_interface2 = actual_interface2;
									}
								}
							}
						}
						// otherwise we need to establish a new lightpath on this interface
						else
						{
							// check if the interface has capacity to carry the connection (possibility of grooming in term of capacity)
							if (used_capacity[node_id_endpoint2 - 1][interface_ind] + connection_capacity <= capacity2)
							{
								// save status of the interface showing that it is used and there is a lightpath established on it
								is_used[node_id_endpoint2 - 1][interface_ind] = true;

								// add the used capacity
								used_capacity[node_id_endpoint2 - 1][interface_ind] += connection_capacity;

								// save the other endpoint of the lightpath 
								// (we need to know this because for other connections we want to check the possibility of grooming)
								other_end_inds[node_id_endpoint2 - 1][interface_ind] = LP_endpoint1;

								// save that our connection has been routed successfully in the first end-point interface
								is_routed_endpoint2 = true;


								actual_interface2 = (node_id_endpoint2 * 1000) + actual_interfaces[interface_ind];

								if (k == LPs_vector.size() - 1)
								{
									client_actual_interface2 = actual_interface2;
								}
							}
						}
					}
				}

				actual_LPs_vector.push_back(make_tuple(actual_interface1, actual_interface2));
				// check if the connection could be routed on both end-points of the current lightpath
				// either groomed wih other connections or routed on a new established lightpath
				if (is_routed_endpoint1 && is_routed_endpoint2)
				{
					

					// save that the connection is routed on the current lightpath(k)
					is_routed[k] = true;

					// preparing list of lightpaths for printing and saving the results
					if (print_results || true)
					{
						vector<Lightpath*>::const_iterator lp_itr;
						bool found_lp = false;
						for (lp_itr = total_lps.begin(); lp_itr != total_lps.end(); lp_itr++) 
						{
							if ((*lp_itr)->getEndId1() == actual_interface1 && (*lp_itr)->getEndId2() == actual_interface2)
							{
								found_lp = true;
								(*lp_itr)->insert_connection(i);
								(*lp_itr)->add_used_capacity(connection_capacity);
								break;
							}
							if ((*lp_itr)->getEndId1() == actual_interface2 && (*lp_itr)->getEndId2() == actual_interface1)
							{
								found_lp = true;
								(*lp_itr)->insert_connection(i);
								(*lp_itr)->add_used_capacity(connection_capacity);
								break;
							}
						}
						if (found_lp == false)
						{
							vector <Unifiber*> usedFibersinLightpath;
							vector<Unifiber*>::const_iterator fiber_itr;
							int x = 0, y = 0;
							for (int i = 0; i < main_path.size() - 1; i++)
							{
								bool flag = false;
								if (main_path[i] % 100 == 59 && main_path[i + 1] % 100 == 49)
								{
									x = main_path[i];
									y = main_path[i + 1];
									flag = true;
								}
								else if (main_path[i] % 100 == 49 && main_path[i + 1] % 100 == 59)
								{
									x = main_path[i];
									y = main_path[i + 1];
									flag = true;
								}
								else if (main_path[i] % 100 == 49 && main_path[i + 1] % 100 == 49)
								{
									x = main_path[i];
									y = main_path[i + 1];
									flag = true;
								}
								else if (main_path[i] % 100 == 59 && main_path[i + 1] % 100 == 59)
								{
									x = main_path[i];
									y = main_path[i + 1];
									flag = true;
								}
								
								if (flag == true)
								{
									for (fiber_itr = uni_fibers.begin(); fiber_itr != uni_fibers.end(); fiber_itr++) 
									{
										if (x == (*fiber_itr)-> getSrcId() && y == (*fiber_itr)-> getDstId())
										{
											usedFibersinLightpath.push_back(*fiber_itr);
										}
									}	
								}
							}

							total_lps.push_back(new Lightpath(actual_interface1, actual_interface2, lp_type, usedFibersinLightpath));
							total_lps[total_lps.size() - 1]->insert_connection(i);
							total_lps[total_lps.size() - 1]->add_used_capacity(connection_capacity);
						}
					}
				}
			}
			

			// check and save if the connection is routed properly or not
			// we need to check the routing status of the connection in each lightpath
			// the connection is considered routed only if it could be routed into all lightpaths
			/* Example:
			assume we have a connection request from node1 to node5 and the selected path by GA is:
			"100,195,159,249,291,200,295,259,349,391,300,395,359,449,491,400,495,459,549,591,500"
			the corresponding lightpaths which are needed to be established are: 
			(195, 291), (295, 391), (395, 491), (495, 591)
			so for routing the connection into this path we need to be able to route it into all of these lightpaths
			and if for instance we could not to route it into (395, 491), it means that the connection is not routed
			*/

			bool is_connection_routed = true;
			for (int j = 0; j < LPs_vector.size(); j++)
			{
				if (is_routed[j] == false)
				{
					is_connection_routed = false;
					break;
				}
			}
			

			is_connections_routed[i] = is_connection_routed;

			//cout<<"This is th LP size " << actual_LPs_vector.size()<<endl;
			//cin.ignore();
			
			for (int j = 0; j < actual_LPs_vector.size() - 1; j++)
			{
				int current_LP_endpoint2 = get<1> (actual_LPs_vector[j]);
				int current_LP_interface_id_endpoint2 = current_LP_endpoint2 % 1000;
				int current_LP_Node = current_LP_endpoint2 / 1000;
				int next_LP_endpoint1 = get<0> (actual_LPs_vector[j + 1]);
				int next_LP_interface_id_endpoint1 = next_LP_endpoint1 % 1000;
				int next_LP_Node = next_LP_endpoint1 / 1000; 
				

				for (int index = 0; index < total_colored_interfaces; index ++)
				{
					if (actual_interfaces[index] == current_LP_interface_id_endpoint2)
					{
						drop_add[current_LP_Node - 1][index] = true;
						drop_add_capacity[current_LP_Node - 1][index] += connection_capacity;
						break;
					}

					else if (actual_interfaces[index] == next_LP_interface_id_endpoint1)
					{
						drop_add[next_LP_Node - 1][index] = true;
						drop_add_capacity[next_LP_Node - 1][index] += connection_capacity;
						break;
					}
				}
			}

			// get the source node id and destination node id of the current connection request
			int connection_src_node = client_actual_interface1 / 1000;
			int connection_dst_node = client_actual_interface2 / 1000;

			// get the source interface id and destination interface id of the selected path for the current connection request
			int connection_src_interface = client_actual_interface1 % 1000;
			int connection_dst_interface = client_actual_interface2 % 1000;

			for (int index = 0; index < total_number_TPD; index ++)
			{
				if (actual_interfaces[index] == connection_src_interface)
				{
					if (connection_capacity > 10)
					{
						tpd_access_ports_needed[connection_src_node - 1][index] ++;
					}
					else if (connection_capacity <= 10)
					{
						otu4_access_ports_needed[connection_src_node - 1][index] ++;
					}
				}
			}
			for (int index = 0; index < total_number_TPD; index ++)
			{

				if (actual_interfaces[index] == connection_dst_interface)
				{
					if (connection_capacity > 10)
					{
						tpd_access_ports_needed[connection_dst_node - 1][index] ++;
					}
					else if (connection_capacity <= 10)
					{
						otu4_access_ports_needed[connection_dst_node - 1][index] ++;
					}
				}
			}

			for (int index = 0; index < total_number_OTU2; index ++)
			{
				for (int int_index = 0; int_index < 4; int_index ++)
				{
					if (actual_interfaces[total_number_TPD + (index * 4) + int_index] == connection_src_interface)
					{
						otu2_access_ports_needed[connection_src_node - 1][index] ++;
						//break;
					}

					if (actual_interfaces[total_number_TPD + (index * 4) + int_index] == connection_dst_interface)
					{
						otu2_access_ports_needed[connection_dst_node - 1][index] ++;
						//break;
					}
				}
			}	
		}

		baseline_run ++;

		vector<Lightpath*>::const_iterator lp_itr;
		vector<Unifiber*>::reverse_iterator fiber_itr;
		vector<Unifiber*>::const_iterator fiber_itr1;
		vector<Lightpath*> total_full_lps;
		for (lp_itr = total_lps.begin(); lp_itr != total_lps.end(); lp_itr++) 
		{
			total_full_lps.push_back((*lp_itr));

			vector<Unifiber*> opposite_fiber;
			for (fiber_itr = (*lp_itr)->fibers.rbegin(); fiber_itr != (*lp_itr)->fibers.rend(); fiber_itr++) 
			{	
				for (fiber_itr1 = uni_fibers.begin(); fiber_itr1 != uni_fibers.end(); fiber_itr1++) 
				{	
					if ((*fiber_itr)->getSrcId() == (*fiber_itr1)->getDstId() && (*fiber_itr)->getDstId() == (*fiber_itr1)->getSrcId())
					{
						opposite_fiber.push_back((*fiber_itr1));
					}

				}
			}
			
			total_full_lps.push_back(new Lightpath((*lp_itr)->getEndId2(), (*lp_itr)->getEndId1(), (*lp_itr)->getType(), opposite_fiber));	
		}

		total_lps = total_full_lps;

		final_lps = total_lps;
		//float oa_feasibility = oa_baseline_mode(total_lps);
		vector <bool> unfeasible_check = oa_baseline_mode(total_lps);
		// cout << unfeasible_check.size() <<endl;

		//  cout << "unf before: " << unf_demands_before_oa << endl;
		//  cout << "unf after: " << unf_demands_after_oa << endl;
		//  cin.ignore();
		// cout<< "score" << score1<<endl;
		// cin.ignore();

		// define two variables for calculating the feasibility of the solution
		// for every constraint we increment the total_score so at the end we know how many checks we have done
		// but we increment the score only if the constraint is passed 
		// at the end the feasibility will be the score / total_score
		score = 0;  
		total_score = 0;
		all_LPs_OA_feasible = true;

		for(int i = 0 ; i < unfeasible_check.size(); i++)
		{
			if (unfeasible_check[i] == false)
			{
				all_LPs_OA_feasible = false;
				break;
			}
		}
	}
	if (all_LPs_OA_feasible == false)
	{
		total_score += 1;
	}
	// // *************************************************************************
	// // ******************************* END OF THE 100G check for grooming *************************

	bool cards_100g[number_nodes][total_number_TPD];
	int number_100G_card = 0;

	bool cards_200g[number_nodes][total_number_TPD];
	int number_200G_card = 0;

	int number_100G_LP = 0;
	int number_200G_LP = 0;

	bool tpd_boards[number_nodes][total_number_TPD];
	int number_tpd_boards = 0;

	bool otu4_boards_1[number_nodes][total_number_TPD];
	int number_otu4_boards_1 = 0;

	bool otu4_boards_2[number_nodes][total_number_TPD];
	int number_otu4_boards_2 = 0;

	bool otu2_boards[number_nodes][total_number_OTU2];
	int otu2_placed_boards = 0;
	int interface10G = 0;

	int number_motherboard_filter = 0;
	int number_single_filter = 0;

	int number_dcu = 0;

	int number_additional_common = 0;

	for (int i = 0; i < number_nodes; i++)
	{
		for (int j = 0; j < total_number_TPD; j++)
		{
			cards_100g[i][j] = false;
			cards_200g[i][j] = false;
			tpd_boards[i][j] = false;
			otu4_boards_1[i][j] = false;
			otu4_boards_2[i][j] = false;
		}
		for (int j = 0; j < total_number_OTU2; j++)
		{
			otu2_boards[i][j] = false;
		}
	}

	
	// go through the nodes and place boards
	for (int i = 0; i < number_nodes; i++)
	{
		for (int tpd_index = 0; tpd_index < number_TPD_left; tpd_index++)
		{
			// check tpd card left, if it is used 
			if (is_used[i][tpd_index])
			{
				tpd_boards[i][tpd_index] = true;
				// for placing otu4 we need to check the used capacity of the tpd card
				// if it is filled less than 100G 
				if (used_capacity[i][tpd_index] <= 100)
				{
					cards_100g[i][tpd_index] = true;
					number_100G_card ++; // add the number of 100G card used in the entire network
				}
				else 
				{
					cards_200g[i][tpd_index] = true;
					number_200G_card ++; // add the number of 200G card used in the entire network
				}
			}
		}

		for (int tpd_index = number_TPD_left; tpd_index < total_number_TPD; tpd_index++)
		{
			// check tpd card left, if it is used 
			if (is_used[i][tpd_index])
			{
				// both tpd board left and right need to be placed
				tpd_boards[i][tpd_index] = true;
			
				// for placing otu4 we need to check the used capacity of the tpd card
				// if it is filled less than 100G 
				if (used_capacity[i][tpd_index] <= 100)
				{
					cards_100g[i][tpd_index] = true;
					number_100G_card ++; // add the number of 100G card used in the entire network
				}
				else 
				{
					cards_200g[i][tpd_index] = true;
					number_200G_card ++; // add the number of 200G card used in the entire network
				}
			}
		}

		for (int tpd_index = 0; tpd_index < total_number_TPD; tpd_index++)
		{
			if (tpd_boards[i][tpd_index])
			{
				number_tpd_boards ++;
			}	
		}


		int clients_connected_tpds[total_number_TPD] = {0};

		for (int tpd_index = 0; tpd_index < total_number_TPD; tpd_index++)
		{
			if (tpd_access_ports_needed[i][tpd_index] + clients_connected_tpds[tpd_index] <= 2)
			{
				// connect all to the otu2 left (means adding the number of connected client ports)
				clients_connected_tpds[tpd_index] += tpd_access_ports_needed[i][tpd_index];

				// we have managed to connect all of them so, put it 0
				tpd_access_ports_needed[i][tpd_index] = 0;
			}
			else
			{	
				// connect only some of them so that it does not exceed 2
				tpd_access_ports_needed[i][tpd_index] -= 2 - clients_connected_tpds[tpd_index];

				// now 2 clients are connected
				clients_connected_tpds[tpd_index] = 2;
			}
		}

		int clients_connected_otu4_1[total_number_TPD] = {0};
		int clients_connected_otu4_2[total_number_TPD] = {0};

		for (int otu4_index = 0; otu4_index < total_number_TPD; otu4_index++)
		{
			if (otu4_access_ports_needed[i][otu4_index] + clients_connected_otu4_1[otu4_index] <= total_number_TPD)
			{
				// connect all to the otu2 left (means adding the number of connected client ports)
				clients_connected_otu4_1[otu4_index] += otu4_access_ports_needed[i][otu4_index];

				// we have managed to connect all of them so, put it 0
				otu4_access_ports_needed[i][otu4_index] = 0;
			}
			else
			{	
				// connect only some of them so that it does not exceed 2
				otu4_access_ports_needed[i][otu4_index] -= total_number_TPD - clients_connected_otu4_1[otu4_index];

				// now 2 clients are connected
				clients_connected_otu4_1[otu4_index] = total_number_TPD;

				if (otu4_access_ports_needed[i][otu4_index] + clients_connected_otu4_2[otu4_index] <= total_number_TPD)
				{
					// connect all to the otu2 left (means adding the number of connected client ports)
					clients_connected_otu4_2[otu4_index] += otu4_access_ports_needed[i][otu4_index];

					// we have managed to connect all of them so, put it 0
					otu4_access_ports_needed[i][otu4_index] = 0;
				}
				else
				{	
					// connect only some of them so that it does not exceed 2
					otu4_access_ports_needed[i][otu4_index] -= total_number_TPD - clients_connected_otu4_2[otu4_index];

					// now 2 clients are connected
					clients_connected_otu4_2[otu4_index] = total_number_TPD;
				}
			}
		}

		

		for (int otu4_index = 0; otu4_index < total_number_TPD; otu4_index++)
		{
			if (clients_connected_otu4_1[otu4_index] > 0)
			{
				otu4_boards_1[i][otu4_index] = true;
			}
			if (clients_connected_otu4_2[otu4_index] > 0)
			{
				otu4_boards_2[i][otu4_index] = true;
			}
		}


		for (int tpd_index = 0; tpd_index < total_number_TPD; tpd_index++)
		{
			if (drop_add[i][tpd_index])
			{
				if (drop_add_capacity[i][tpd_index] < 100)
				{
					otu4_boards_1[i][tpd_index] = true;
				}
				else if (drop_add_capacity[i][tpd_index] <= 200)
				{
					otu4_boards_1[i][tpd_index] = true;
					otu4_boards_2[i][tpd_index] = true;
				}
			}
		}

		for (int otu4_index = 0; otu4_index < number_TPD_left; otu4_index++)
		{
			if (otu4_boards_1[i][otu4_index])
			{
				//otu4_boards_1[i][5] = true;
				number_otu4_boards_1 += 1;
				//number_additional_common ++;
			}
			if (otu4_boards_2[i][otu4_index])
			{
				//otu4_boards_2[i][5] = true;
				number_otu4_boards_2 += 1;
				//number_additional_common ++;
			}
		}

		for (int otu4_index = number_TPD_left; otu4_index < total_number_TPD; otu4_index++)
		{
			if (otu4_boards_1[i][otu4_index])
			{
				//otu4_boards_1[i][5] = true;
				number_otu4_boards_1 += 1;
				//number_additional_common ++;
			}
			if (otu4_boards_2[i][otu4_index])
			{
				//otu4_boards_2[i][5] = true;
				number_otu4_boards_2 += 1;
				//number_additional_common ++;
			}
		}


		for (int otu4_index = 0 ; otu4_index < number_TPD_left; otu4_index++)
		{
			if (otu4_boards_1[i][otu4_index] || otu4_boards_1[i][number_TPD_left + otu4_index])
			{
				number_additional_common ++;
			}
			if (otu4_boards_2[i][otu4_index] || otu4_boards_2[i][number_TPD_left + otu4_index])
			{
				number_additional_common ++;
			}
		}

		for (int tpd_index = 0; tpd_index < number_TPD_left; tpd_index++)
		{
			if (tpd_boards[i][tpd_index] || tpd_boards[i][number_TPD_left + tpd_index])
			{
				number_additional_common ++;
			}
		}


		for (int  j = 0; j < number_OTU2_left; j++)
		{
			for (int otu2l_index = 0; otu2l_index < 4; otu2l_index++)
			{
				if (is_used[i][total_number_TPD + (j*4) + otu2l_index])
				{
					otu2_boards[i][j] = true;
					interface10G ++;
					number_single_filter ++;	
				}
			}
		}

		for (int  j = number_OTU2_left; j < total_number_OTU2; j++)
		{
			for (int otu2r_index = 0; otu2r_index < 4; otu2r_index++)
			{
				if (is_used[i][total_number_TPD + (j*4) + otu2r_index])
				{
					otu2_boards[i][j] = true;
					interface10G ++;
					number_single_filter ++;
				}
			}	
		}

		for (int otu2_ind = 0; otu2_ind < total_number_OTU2; otu2_ind++)
		{
			if (otu2_boards[i][otu2_ind])
			{
				otu2_placed_boards ++;
				number_motherboard_filter ++;
			}

		}

		for (int otu2_ind = 0; otu2_ind < number_OTU2_left; otu2_ind++)
		{
			if (otu2_boards[i][otu2_ind] || otu2_boards[i][number_OTU2_left + otu2_ind])
			{
				number_additional_common ++;
			}

		}

		int number_unconnected_requests = 0;
		int number_connected_requests = 0;

		for (int tpd_index = 0; tpd_index < total_number_TPD; tpd_index++)
		{
		
			number_unconnected_requests += tpd_access_ports_needed[i][tpd_index] ;

			number_connected_requests += clients_connected_tpds[tpd_index];
		}

		for (int otu4_index = 0; otu4_index < total_number_TPD; otu4_index++)
		{
		
			number_unconnected_requests += otu4_access_ports_needed[i][otu4_index];

			number_connected_requests += clients_connected_otu4_1[otu4_index] + clients_connected_otu4_2[otu4_index];
		}

		total_score += number_connected_requests + number_unconnected_requests;	
		score += number_connected_requests;
	}
	if (interface10G > 0)
	{
		number_dcu = number_uni_fibers * 2;
	}

	if (ari_debug)
	{
		cout << "total score 1 -> " << total_score << endl;
		cout << "score 1 -> " << score << endl;

		cout << "unrouted connections" << endl;
	}
	// check if all connection requests are routed
	for (int i = 0; i < number_connection_requests; i++)
	{
		if (is_connections_routed[i])
		{
			score ++;
			total_score ++;
		}
		else
		{
			if (ari_debug)
			{
				cout << i << " ";
			}
			total_score ++;
		}
	}
	if (ari_debug)
	{
		cout << endl;

		cout << "total score 2 -> " << total_score << endl;
		cout << "score 2 -> " << score << endl;
	}

	// check the number of wavelengths
	number_100G_LP = number_100G_card / 2;
	number_200G_LP = number_200G_card / 2;


	if (number_100G_LP + number_200G_LP <= number_lambdas)
	{
		score ++;
		total_score ++;
	}
	else
	{
		total_score ++;
	}

	if (ari_debug)
	{
		cout << "total score 3 -> " << total_score << endl;
		cout << "score 3 -> " << score << endl;
	}

	// calculate the feasibility
	feasibility = score / total_score;
	//cout<< "Feasibility" << feasibility << endl;
	// now the placed and used components (boards, interfaces, tpd cards, ...) are available
	// so we need to calculate the fitness value
	// depending on the objctive (it's an input parameter for the software) 
	// objective 0 means only cost, so we consider the relative cost values for each component 
	if (objective == 0)
	{
		fitness += otu2_placed_boards * float(3.1);

		fitness += interface10G * float(0.7);

		fitness += number_tpd_boards * float(2.5);

		fitness += (number_otu4_boards_1 + number_otu4_boards_2) * float(3.8);

		fitness += number_100G_card * float(5.0);

		fitness += number_200G_card * float(6.12);

		fitness += number_additional_common * float(0.95);

		fitness += number_dcu * float(0.59);

		fitness += number_motherboard_filter * float(0.37);

		fitness += number_single_filter * float(0.45);
	}
	// check if we need to prepare the results
	if (print_results)
	{
		ofstream result_file(result_file_n, std::ios_base::app | std::ios_base::out);
		result_file << endl << "-------------------------- RESULTS --------------------------" << endl << endl;
		result_file << "### Total components in the entire network: " << endl;

		result_file << "- Number of OTU2 boards: " << otu2_placed_boards << endl;

		result_file << "- Number of 10G interfaces: " << interface10G << endl;

		result_file << "- Number of TPD boards: " << number_tpd_boards << endl;

		result_file << "- Number of OTU4 boards: " << number_otu4_boards_1 + number_otu4_boards_2 << endl;

		result_file << "- Number of 100G cards: " << number_100G_card << endl;

		result_file << "- Number of 200G cards: " << number_200G_card << endl;

		result_file << "- Number of DCUs: " << number_dcu << endl;

		result_file << "- Number of single channel filters: " << number_single_filter << endl;

		result_file << "- Number of motherboard filters: " << number_motherboard_filter << endl;

		result_file << "- Number of common parts: " << number_additional_common << endl << endl;

		vector<Lightpath*>::const_iterator lp_itr;
		vector<Lightpath*>::const_iterator lp_itr_2;

		int lambda = 0;
		for (lp_itr = total_lps.begin(); lp_itr != total_lps.end(); lp_itr++) 
		{
			// cout << (*lp_itr)->getEndId1() << endl;
			// cout << (*lp_itr)->getEndId2() << endl;
			// cout << (*lp_itr)->getType() << endl;
			// cout << (*lp_itr)->candidate_paths.size() << endl;
			// cout << "--------------------------------" << endl;
			// cin.ignore();
			int node_id = (*lp_itr)->getEndId1() / 100;
			int interface_id = (*lp_itr)->getEndId1() % 100;
			int interface_index;
			int lp_type = 0;
			bool tpd100_200 = false;
			switch (interface_id)
			{
				case 47: // if it is routed on 10G interface left
				{
					interface_index = 0;
					tpd100_200 = true;
					break;
				}

				case 81: // if it is routed on 10G interface right
				{
					interface_index = 1;
					tpd100_200 = true;
					break;	
				}

				case 82: // if it is routed on tpd card left
				{	
					interface_index = 2;
					tpd100_200 = true;
					break;
				}

				case 83: // if it is routed on tpd card right
				{
					interface_index = 3;
					tpd100_200 = true;
					break;
				}

				case 84: // if it is routed on tpd card right
				{
					interface_index = 4;
					tpd100_200 = true;
					break;
				}

				case 48: // if it is routed on 10G interface left
				{
					interface_index = 5;
					tpd100_200 = true;
					break;
				}

				case 85: // if it is routed on 10G interface right
				{
					interface_index = 6;
					tpd100_200 = true;
					break;	
				}

				case 86: // if it is routed on tpd card left
				{	
					interface_index = 7;
					tpd100_200 = true;
					break;
				}

				case 87: // if it is routed on tpd card right
				{
					interface_index = 8;
					tpd100_200 = true;
					break;
				}

				case 88: // if it is routed on tpd card right
				{
					interface_index = 9;
					tpd100_200 = true;
					break;
				}

				default:
				{
					lp_type = 10;
				}
			}
			if (tpd100_200)
			{
				if (cards_100g[node_id - 1][interface_index])
				{
					lp_type = 100;
				}

				else if (cards_200g[node_id - 1][interface_index])
				{
					lp_type = 200;
				}
			}
			
			result_file << "Lambda: " << lambda << " --> " << (*lp_itr)->getEndId1() << " , " << (*lp_itr)->getEndId2();
			result_file << "  " << (*lp_itr)->getType() << "G" << endl;
			result_file << "routed connections on this lp: ";
			for (int i = 0; i < (*lp_itr)->routed_connections.size(); i ++)
			{
				result_file << (*lp_itr)->routed_connections[i] << ", "; 
			}
			result_file << endl << endl;
			lambda ++;
		}

		// vector<Unifiber*>::reverse_iterator fiber_itr;

		// vector<Unifiber*>::const_iterator fiber_itr1;

		// vector<Lightpath*> total_full_lps;
		// for (lp_itr = total_lps.begin(); lp_itr != total_lps.end(); lp_itr++) 
		// {
		// 	total_full_lps.push_back((*lp_itr));

		// 	vector<Unifiber*> opposite_fiber;
		// 	for (fiber_itr = (*lp_itr)->fibers.rbegin(); fiber_itr != (*lp_itr)->fibers.rend(); fiber_itr++) 
		// 	{	
		// 		for (fiber_itr1 = uni_fibers.begin(); fiber_itr1 != uni_fibers.end(); fiber_itr1++) 
		// 		{	
		// 			if ((*fiber_itr)->getSrcId() == (*fiber_itr1)->getDstId() && (*fiber_itr)->getDstId() == (*fiber_itr1)->getSrcId())
		// 			{
		// 				opposite_fiber.push_back((*fiber_itr1));
		// 			}

		// 		}
		// 	}
			
		// 	total_full_lps.push_back(new Lightpath((*lp_itr)->getEndId2(), (*lp_itr)->getEndId1(), (*lp_itr)->getType(), opposite_fiber));	
		// }

		// total_lps = total_full_lps;

		lambda = 0;
		float sum = 0;
		for (lp_itr = total_lps.begin(); lp_itr != total_lps.end(); lp_itr++) 
		{
			(*lp_itr)->set_id(lambda);
			lambda ++;
			sum += (*lp_itr)->get_lp_length();
			//cout << "length" <<(*lp_itr)->get_lp_length();
		}

		cout<< "Avg lenght is " << sum/lambda <<endl;


		result_file << "Cost: " << fitness << endl << endl;
		result_file << "feasibility: " << feasibility << endl << endl;
		result_file << "### List of components in each node:" << endl;
		result_file.close();


		cout << "-----------------------------------------" << endl;
		cout << "-----------------------------------------" << endl;
		cout << "---------------OTN finished--------------" << endl;
		cout << "-----------------------------------------" << endl;
		cout << "-----Cheking QoT for all lightpaths------" << endl;

		final_lps = total_lps;
		
		//float reachedhere = OAPlacement();
		//cout << "OA Best cost: " << reachedhere << endl;
	}

	return make_tuple(feasibility, fitness);
}


vector<vector<int> > Network::mutation_importance()
{
	// this function creates a matrix containing group indexes
	// to give more importance to those groups when GA is mutating the genes
	// can be changed to see the impact of important groups

	vector<vector<int> > important_mutation_modes_matrix;

	vector<int> important_mutation_modes;

	if (number_nodes < 5)
	{
		important_mutation_modes = {1};
	}

	else if (number_nodes == 5)
	{
		if (connection_requests.size() < 25)
		{
			important_mutation_modes = {1};
		}

		else
		{
			important_mutation_modes = {0, 1};
		}
	}
	else if (number_nodes == 6)
	{
		if (connection_requests.size() < 55)
		{
			if (objective == 1)
				important_mutation_modes = {0};
		}

		else
		{
			important_mutation_modes = {0};
		}
	}

    for (int i = 0; i < number_connection_requests; i ++)
    {
		important_mutation_modes_matrix.push_back(important_mutation_modes);
    }	

	return important_mutation_modes_matrix;
}

////// What ari recently added......................................

void Network :: CheckOBSolution()
{
	vector <Unifiber*> :: iterator itrfiber;
	vector <Lightpath*> :: iterator lp_itr;
	vector <Lightpath*> LPS;
	
	for(itrfiber = uni_fibers.begin(); itrfiber != uni_fibers.end(); itrfiber++)
	{
		int interface1, interface2, id, lp_type;
		vector<Unifiber*> fibers_in_lp;

		if((*itrfiber)->getSrcId() == 159 && (*itrfiber)->getDstId() == 249 )
		{
			interface1 = 148;
			interface2 = 247;
			id = 0;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));
		}
		if((*itrfiber)->getSrcId() == 249 && (*itrfiber)->getDstId() == 159)
		{
			interface1 = 247;
			interface2 = 148;
			id = 1;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));

		}
		if((*itrfiber)->getSrcId() == 259 && (*itrfiber)->getDstId() == 349)
		{
			interface1 = 248;
			interface2 = 347;
			id = 2;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));

		}
		if((*itrfiber)->getSrcId() == 349 && (*itrfiber)->getDstId() == 259)
		{
			interface1 = 347;
			interface2 = 248;
			id = 3;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));

		}
		if((*itrfiber)->getSrcId() == 359 && (*itrfiber)->getDstId() == 449)
		{
			interface1 = 348;
			interface2 = 447;
			id = 4;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));

		}
		if((*itrfiber)->getSrcId() == 449 && (*itrfiber)->getDstId() == 359)
		{
			interface1 = 447;
			interface2 = 348;
			id = 5;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));
		}
		if((*itrfiber)->getSrcId() == 459 && (*itrfiber)->getDstId() == 549)
		{
			interface1 = 448;
			interface2 = 547;
			id = 6;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));

		}
		if((*itrfiber)->getSrcId() == 549 && (*itrfiber)->getDstId() == 459)
		{
			interface1 = 547;
			interface2 = 448;
			id = 7;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));

		}
		if((*itrfiber)->getSrcId() == 559 && (*itrfiber)->getDstId() == 149)
		{
			interface1 = 548;
			interface2 = 147;
			id = 8;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));

		}
		if((*itrfiber)->getSrcId() == 149 && (*itrfiber)->getDstId() == 559)
		{
			interface1 = 147;
			interface2 = 548;
			id = 9;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));
		}

		Lightpath *lp1 = new Lightpath(interface1, interface2, lp_type, fibers_in_lp);
		lp1->set_id(id);
		LPS.push_back(lp1);	
	}

	
	vector<Unifiber*> temp_fibers;
	for(itrfiber = uni_fibers.begin(); itrfiber != uni_fibers.end(); itrfiber++)
	{
		int interface1, interface2, id, lp_type;
		vector<Unifiber*> fibers_in_lp;
		

		if((*itrfiber)->getSrcId() == 159 && (*itrfiber)->getDstId() == 249 )
		{
			interface1 = 148;
			interface2 = 247;
			id = 10;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));
				Lightpath *lp2 = new Lightpath(interface1, interface2, lp_type, fibers_in_lp);
			lp2->set_id(id);
			LPS.push_back(lp2);
		}

		if((*itrfiber)->getSrcId() == 249 && (*itrfiber)->getDstId() == 159 )
		{
			interface1 = 247;
			interface2 = 148;
			id = 11;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));
				Lightpath *lp2 = new Lightpath(interface1, interface2, lp_type, fibers_in_lp);
			lp2->set_id(id);
			LPS.push_back(lp2);
		}
		
		if((*itrfiber)->getSrcId() == 259 && (*itrfiber)->getDstId() == 349)
		{
			interface1 = 248;
			interface2 = 347;
			id = 12;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));
				Lightpath *lp2 = new Lightpath(interface1, interface2, lp_type, fibers_in_lp);
			lp2->set_id(id);
			LPS.push_back(lp2);

		}

		if((*itrfiber)->getSrcId() == 349 && (*itrfiber)->getDstId() == 259)
		{
			interface1 = 347;
			interface2 = 248;
			id = 13;
			lp_type = 100;
			fibers_in_lp.push_back((*itrfiber));
			Lightpath *lp2 = new Lightpath(interface1, interface2, lp_type, fibers_in_lp);
			lp2->set_id(id);
			LPS.push_back(lp2);

		}

			
	}

	for(itrfiber = uni_fibers.begin(); itrfiber != uni_fibers.end(); itrfiber++)
	{
		if ((*itrfiber)->getSrcId() == 359 && (*itrfiber)->getDstId() == 449)
		{
			temp_fibers.push_back((*itrfiber));
		}

		else if ((*itrfiber)->getSrcId() == 459 && (*itrfiber)->getDstId() == 549)
		{
			temp_fibers.push_back((*itrfiber));
		}

		else if ((*itrfiber)->getSrcId() == 559 && (*itrfiber)->getDstId() == 149)
		{
			temp_fibers.push_back((*itrfiber));
		}
	}


	Lightpath *lp3 = new Lightpath(348, 147, 100, temp_fibers);
	lp3->set_id(14);
	LPS.push_back(lp3);	



	temp_fibers.clear();
	for(itrfiber = uni_fibers.begin(); itrfiber != uni_fibers.end(); itrfiber++)
	{
		if ((*itrfiber)->getSrcId() == 149 && (*itrfiber)->getDstId() == 559)
		{
			temp_fibers.push_back((*itrfiber));
		}

		else if ((*itrfiber)->getSrcId() == 549 && (*itrfiber)->getDstId() == 459)
		{
			temp_fibers.push_back((*itrfiber));
		}

		else if ((*itrfiber)->getSrcId() == 449 && (*itrfiber)->getDstId() == 359)
		{
			temp_fibers.push_back((*itrfiber));
		}
	}

	Lightpath *lp4 = new Lightpath(147, 348, 100, temp_fibers);
	lp4->set_id(15);
	LPS.push_back(lp4);	
	


	final_lps = LPS;

	double getQoT = 0;
	double osnr_tot = 0;
	cout << "calculating QoT for OB!" << endl;
	for (lp_itr = final_lps.begin(); lp_itr != final_lps.end(); lp_itr++) 
	{
		QoTcalc2((*lp_itr));
		//cout << "lightpath " << (*lp_itr)->get_id() << ", QoT : " << getQoT << endl;
	}

	cout << "starting OA for OB!" << endl;
	cout << "there are " << getSizeOfUnfeasible() << " unfeasible lightpaths!" << endl;

	if (getSizeOfUnfeasible() != 0)
	{
		int reachedhere = OAPlacement();
	}
	
}

//******************************************************************************************
//QoT calculation function for the configuration in which there is no Optical Amplifier added to the network yet

double Network :: QoTcalc2(Lightpath *lp)
{
	double gamma = 1.3;
	double PI = 3.1415926;
	double c_band = 5 * pow(10,12);
	double beta_2n = 21 * pow(10,-24);
	double Planck = 6.62607004 * pow(10, -34); //h -Planck's constant
	double centFreq = 193.1 * pow(10, 12); //central propagating frequency
	double NF = 6; //Noise Figure dB
	double NF_lin = pow(10, (NF/10)); //NF linear

	double Rs = 32 * pow(10,9); //Symbol rate is taken to be 32GBaud; 32*log2(M=16)*10^9 = 128*10^9
	double Bn = 12.5 * pow(10,9); //osnr noise reference bandwidth Bn=0.1nm which is approx. equal to 3THz


	//QoT calculation in the first step when there are no line amplifiers deployed in the network and the only amplfiers
	//in the network are the pre-amplifiers placed in the nodes
	//list<AbstractLink*> :: iterator itr2;
	
	// initialize the pathLength as zero at the begining of each demand
	int pathLength = 0;
	int pathLength_km = 0; 
	
	vector<Unifiber*> :: iterator itr_1;

	for (itr_1 = lp->fibers.begin(); itr_1 != lp->fibers.end(); itr_1++)
	{
		pathLength += (*itr_1)->getLength() + node_loss_km;
		pathLength_km += (*itr_1)->getLength();
	}

	OA_file << pathLength_km << " km - ";
	OA_file << pathLength * loss_coeff << " dB" << endl;
/*
	cout << pathLength_km << " km - ";
	cout << pathLength * loss_coeff << " dB" << endl;
	cin.ignore();
*/

	if (pathLength_km < min_path_km)
		min_path_km = pathLength_km;

	if (pathLength_km > max_path_km)
		max_path_km = pathLength_km;

	sum_paths_km += pathLength_km;
	avg_path_km = sum_paths_km / final_lps.size();

	sum_paths_loss += pathLength * loss_coeff;

	loss_coeff = 0.25;
	// compute the OSNR
	double spanloss = pathLength * loss_coeff;
	double spanloss_lin = pow(10, (spanloss/10));
	double alpha_linear = loss_coeff * (log(10)/10);

	double eff_length = (1 - exp(-2 * alpha_linear * pathLength)) / (2 * alpha_linear); 

	double asinh_func = asinh((pow(PI,2) / (4 * alpha_linear)) * beta_2n * (pow(c_band,2)));  
	double expression = ((alpha_linear * gamma * gamma * eff_length * eff_length) / (PI * beta_2n));
	double nli_coeff = spanloss_lin* ((double)16/27) * expression * asinh_func;   

	double pow_i = (Planck * centFreq * spanloss_lin * NF_lin) / (2 * nli_coeff);
	double pow_opt = cbrt(pow_i);
	double power_mW = pow_opt * Rs * pow(10,3);
	double power_dBm = 10 * log10(power_mW);

	double osnr_nl = (pow_opt * Rs) / (Bn * nli_coeff * pow(pow_opt,3));
	double osnr_tot = (1 / osnr_nl);

	double Prec = power_dBm - spanloss;

	double QoT_value = Prec; //12JUNE19



	if(QoT_value < -18) //12JUNE19  
	{
		//different with the one up "unfeasibleDemands" cause this is a list of pointers of type pCon
		listUD.push_back(lp); 

		for (itr_1 = lp->fibers.begin(); itr_1 != lp->fibers.end(); itr_1++)
		{
			// in oder not to push_back the same link twice in the list of links 
			// that have unfeasible demands passing through
			if(find(listUL.begin(), listUL.end(), ((*itr_1))) == listUL.end())
						listUL.push_front((*itr_1));
		}
	}

	//allDemands.push_back(pCon);
	
	OA_file.close();

    return QoT_value;
}


// computations are stopped after each placement
// starting with the ones from OA_GA_init.txt
// feasibilities are written into OA_GA_OSNR.txt
#define DEBUG_PLACEMENT 0
#define FULL_OPTIMIZATION 1	// OSNRs of unfeasible demands might be incorrect
#define GEN_FAST_RUN 20


// *************************************************************************************************************************
double Network :: OAPlacement(bool fast_run)
{

	// baseline placement is created in the TopoReader, written to "OA_GA_init.txt"
	// and its OSNR is computed and written to "OA_GA_OSNR.txt"
	baseline_mode = false;

	// whether we account for ASE propagation
	filterless = true;
	blockers = true;

	OA_placement_objective = OA_Objective::COST;

    map<int, float> port_loss_map;

	for(int degree = 1; degree < 8; degree ++)
		port_loss_map[degree] = 3 * ceil(log(degree) / log(2));


	// set port_degree in every node of the network (or a tree)
	for(auto node_itr = nodes.begin(); node_itr != nodes.end(); node_itr ++)
	{
		(*node_itr) -> port_loss_dB.clear();
		
		// cannot just use AbstractNode :: m_hILinkList, 
		// as the same node can be included in different filterless trees
		vector<int> adj_links;

		for(auto link_itr = uni_fibers.begin(); link_itr != uni_fibers.end(); link_itr ++)
			if ((*node_itr) -> getID() == (*link_itr) -> dst_node -> getID() or (*node_itr) -> getID() == (*link_itr) -> src_node -> getID() )
				adj_links.push_back((*link_itr)->getId());

		if (adj_links.size() % 2 != 0)
			throw runtime_error("Weird node degree");

		float loss_dB = 0;

		// WSS has a fixed loss, independent on the number of ports
        if(filterless == false)
            loss_dB = filter_loss_dB;

		// splitter/combiner loss depends on the number of ports
        else
            loss_dB = port_loss_map[adj_links.size() / 2];

		// TO CHECK
		if (loss_dB == 0)
			loss_dB = 3;

		for(auto link_itr = adj_links.begin(); link_itr != adj_links.end(); link_itr ++)
		{
			(*node_itr) -> port_loss_dB[*link_itr] = loss_dB;
			(*node_itr) -> port_degree[*link_itr] = adj_links.size() / 2;
        }
	}

	
	ofstream OA_GA_File;
	OA_GA_File.open ("OA_GA_results.txt", ios::out | ios::app);
	return getOaLoc_GA(OA_GA_File, fast_run);
}

// ************************************************************************************************************************
// addOaLoc
// added by MEM
// creates the candidate locations for placing the optical amplifiers
OaLoc* Network :: addOaLoc(int OaLocId, int OaLocLink, int OaLocLength, int OaLocInd, double OaGain, double OaNF, int OaType)
{
	//cout<<"\n\n THIS IS A PRINT TEST\n";
	//cout<<"Candidate location: " << OaLocId <<" on fiber: " << OaLocLink << " at distance: " << OaLocLength << " type: " << OaType << endl;
	OaLoc *pOaLoc = new OaLoc(OaLocId, OaLocLink, OaLocLength, OaLocInd, OaGain, OaNF, OaType);
	
	// OLEG
	pOaLoc -> reset(lookUpLinkById(OaLocLink));
	pOaLoc -> m_AccumulatedOSNRperLink.clear();

	// booster is always a booster
	if (pOaLoc -> m_OaType == 1)
		pOaLoc -> m_OaCost = OaLoc :: booster_cost;

	// ILA is initially considered as a booster
	// because booster has lower cost
	else if (pOaLoc -> m_OaType == 2)
		pOaLoc -> m_OaCost = OaLoc :: ILA_booster_cost;

	// preamp may be considered as a booster
	else if (pOaLoc -> m_OaType == 3)
		pOaLoc -> m_OaCost = OaLoc :: preamp_cost;

	OaLocationList.push_back(pOaLoc);

	return pOaLoc;
}


//  *************************************************************************************************************************
// getOaLoc_GA
// places Optical Amplifiers and Power Shapers using genetic algorithm
// in case of fast_run == true only GEN_FAST_RUN generations with a reduced size are evaluated
// apriori placements are taken from "OA_GA_init.txt"
// results are written to "OA_GA_results.txt"

#define QOT_DEBUG_OUTPUT 0

double Network :: getOaLoc_GA(ofstream& LogFile, bool fast_run)
{
	if (filterless and blockers)
	{
		cout << "In" << endl;
		filterless = false;
		//placeFilters(9);
		placeFilters(1);
		filterless = false;

		//OA_OSNR_file << "Filters placed" << endl;
	}

	// logging
	if(fast_run == false)
	{
		// current date/time based on current system
		time_t now = time(0);

		LogFile << endl << endl << "***************************" << endl;
		LogFile << ctime(&now) << "***************************" << endl;
	}

	// population size
	int pop_size = 2000;

	if(fast_run)
		pop_size = 1000;

	if(baseline_mode or DEBUG_PLACEMENT)
		pop_size = 1;

	double best_cost = 1e6;
	auto switch_cost_CU = switching_cost();


	// first define the structure of the chromosome - order of genes (or gene clusters) and their weights
	vector<vector<float>> chromosome_struct;

	vector<float> temp_booster;
	temp_booster.push_back(OaLoc :: booster_cost);

	vector<float> temp_preamp;
	temp_preamp.push_back(OaLoc :: preamp_cost);

	vector<float> temp_ILA;
	temp_ILA.push_back(OaLoc :: ILA_booster_cost);

	// then assign the weights to the locations
	for (auto itrLoc = OaLocationList.begin(); itrLoc != OaLocationList.end(); itrLoc ++)
	{
		// booster
		if ((*itrLoc) -> m_OaType == 1)
			chromosome_struct.push_back(temp_booster);

		// ILA
		else if ((*itrLoc) -> m_OaType == 2)
			chromosome_struct.push_back(temp_ILA);

		// preamp
		else if ((*itrLoc) -> m_OaType == 3)
			chromosome_struct.push_back(temp_preamp);

		else
			throw runtime_error("getOaLoc_GA. Unknown EDFA type");
	}
		
	// construct a GA object
	// GeneticAlgorithm GenAmpPlacement(pop_size, chromosome_struct, GeneticAlgorithm :: OA_placement_single);
	GeneticAlgorithm_OA GenAmpPlacement(pop_size, chromosome_struct, GeneticAlgorithm_OA :: OA_placement_single, false, fast_run);

	// generate random solutions and place baseline as the first one
	GenAmpPlacement.first_generation();
	//GenAmpPlacement.create_solution(create_SNRaware_minOTN_OAplacement(), false, 0);
	

	if(DEBUG_PLACEMENT == true and baseline_mode == false)
	{

	}

	// else
	//	GenAmpPlacement.create_solution(create_baseline_placement(LogFile), false, 0);


	vector<vector<float>> fitness_matrix;
    fitness_matrix.push_back(vector<float>(pop_size));
    fitness_matrix.push_back(vector<float>(pop_size));

	vector<float> feasibility_vect(pop_size);

	// till we've reached a stopping condition
	while (GenAmpPlacement.is_improved())
	{
		// to accound only the unique solutions
		vector<int> matching_list_solutions;

		// choose the unique solutions
		int num_unique = GenAmpPlacement.find_unique_solutions(matching_list_solutions);

		vector<float> unique_fitness_vect(num_unique);
		vector<float> unique_secondary_fitness_vect(num_unique);
				
		// ratio from 0 to 1 for each partition
		vector<float> unique_feasibility_vect(num_unique);

		// go through all the placements of the population
		for (int GA_solution_ind = 0; GA_solution_ind < num_unique; GA_solution_ind ++)
		{
			//cout << "Solution: " << GA_solution_ind << endl;

            unique_feasibility_vect[GA_solution_ind] = 0;

			// go through all the locations and place amplifiers and filters
			for(int gene_ind = 0; gene_ind < OaLocationList.size(); gene_ind ++)
			{
				OaLocationList[gene_ind] -> m_OaLocIndicator = (int)(GenAmpPlacement.is_selected_gene_unique_active(GA_solution_ind, gene_ind));
			}

			OA_OSNR_file.open("OA_OSNR_file.txt", ios::out|ios::trunc);

			if(QOT_DEBUG_OUTPUT)
			{
				// cout << "Solution: " << GA_solution_ind << endl;
				OA_OSNR_file << "Solution: " << GA_solution_ind << endl;
				OA_OSNR_file << "Nodes: ";
				for(auto nodeItr = nodes.begin(); nodeItr != nodes.end(); nodeItr ++)
					OA_OSNR_file << (*nodeItr) -> getID() << ", ";
				OA_OSNR_file << endl;

				OA_OSNR_file << "Links: ";
				for(auto linkItr = uni_fibers.begin(); linkItr != uni_fibers.end(); linkItr ++)
					OA_OSNR_file << (*linkItr) -> getId() << " between " << (*linkItr) -> src_node -> getID() << " and " << (*linkItr) -> dst_node -> getID() << endl;
				OA_OSNR_file << endl;

				for(auto itr_loc = OaLocationList.begin(); itr_loc != OaLocationList.end(); itr_loc ++)
					OA_OSNR_file << "EDFA " << (*itr_loc) -> getOaId() << " at link " << (*itr_loc)->m_OaLocLink << endl;
			
			
				OA_OSNR_file << "Demands routed in this tree: " << endl;
			

				for(auto itrDemand = final_lps.begin(); itrDemand != final_lps.end(); itrDemand ++)
				{
					OA_OSNR_file << "Demand " << (*itrDemand)->get_id() << " from " << (*itrDemand)->getEndId1() << " to " << (*itrDemand)->getEndId2() <<   " routed in this tree " << endl;
					OA_OSNR_file << "Path: ";      
					for(auto itrLink = (*itrDemand)->candidate_paths[0].begin(); itrLink != (*itrDemand)->candidate_paths[0].end(); itrLink ++)
						OA_OSNR_file << (*itrLink) -> getId() << " ";
					OA_OSNR_file << endl;
				}
			}

			//LogFile << "Gain setting" << endl;

			// set the gains in all the network
			bool gain_can_compensate_losses = gainOAfunc(OA_OSNR_file);

			if (baseline_mode and gain_can_compensate_losses == false)
				throw runtime_error("Baseline placement cannot compensate for the losses");

			if(QOT_DEBUG_OUTPUT)
				OA_OSNR_file << "Gain compensates losses: " << gain_can_compensate_losses << endl;


			// pair<double, double> Tx_cost_CU(0, 0);
			// double Tx_CAPEX_year_0_CU = 0;	
			pair<double, double> OA_cost_CU(0, 0);

			double SNR_worst = 1000;
			double SNR_sum = 0;
			
			int num_paths = 0;
			int network_throughput_G = 0;

			//LogFile << "SNR calculation" << endl;


			if (gain_can_compensate_losses)
			{
				for(auto itr_loc = OaLocationList.begin(); itr_loc != OaLocationList.end(); itr_loc ++)
				{
					if ((*itr_loc) -> m_OaLocIndicator == 1)
					{
					  	if ( (*itr_loc) -> gain_dB < 1)
							(*itr_loc) -> m_OaLocIndicator = 0;
			
						else
						{
							OA_cost_CU.first += (*itr_loc) -> m_OaCost;

							// electricity cost
							//if ( (*itr_loc) -> m_OaType == 1 or (*itr_loc) -> m_OaType == 2)
							OA_cost_CU.second += 0.008 * 0.001 * 24 * 365 * 5;
						
							//else if ( (*itr_loc) -> m_OaType == 3)
							//	OA_cost_CU.second += 0.018 * 0.001 * 24 * 365 * 5;
						}
					}
				}
				

				// other costs
				OA_cost_CU.first *= 1.3;
				OA_cost_CU.second *= 1.75;
				//lp_SNR.clear();
				// for each demand
				for(auto itrDemand = final_lps.begin(); itrDemand != final_lps.end(); itrDemand ++)
				{
					if (filterless and (*itrDemand) -> candidate_paths.size() != 1)
						throw runtime_error("IN FON THERE CAN BE ONLY ONE PATH");

					bool all_feasible_paths = true;

					// for each of kSP path
					for(auto itrPath = (*itrDemand)->candidate_paths.begin(); itrPath != (*itrDemand)->candidate_paths.end(); itrPath ++)
					{
						pair<double, double> temp = calculateDemandSNR(OA_OSNR_file, *itrPath, (*itrDemand)->getType());
						
						double SNR_demand = temp.first;
						double P_rx = temp.second;
						//lp_SNR.push_back(SNR_demand);

						// cout << P_rx << endl;
						// cout << SNR_demand << endl;
						// cout << (*itrDemand) ->getType() << endl;
						// cout << (*itrDemand) ->get_id() << endl;
						// cin.ignore();

						// if (SNR_demand < SNR_threshold_dB)
						// 	continue;
						// if((*itrDemand) ->getType() == 10)
						// {
						// 	if (SNR_demand < SNR_threshold_10G)
						// 		continue;
						// }

						// else if((*itrDemand) ->getType() == 100)
						// {
						// 	if (SNR_demand < SNR_threshold_100G)
						// 		continue;
						// }	
						// else if((*itrDemand) ->getType() == 200)
						// {
						// 	if (SNR_demand < SNR_threshold_200G)
						// 		continue;
						// }

						num_paths ++;

						if (OA_placement_objective == OA_Objective::COST)
						{
							int max_bitrate_G = max_possible_throughput(SNR_demand);
							network_throughput_G += max_bitrate_G;

							vector<int> avail_bitrate_G(2, 0);

							if(max_bitrate_G >= 100)
								avail_bitrate_G[0] = 100;
								
							avail_bitrate_G[1] = max_bitrate_G;

							// vector<double> cost_vect_temp;
							// cost_vect_temp = ILP_Tx((*itrDemand) -> m_nChoice, avail_bitrate_G, {5, 12}, 5, 0.2, Tx_ILP_mutex, Tx_ILP_cache);

							// Tx_cost_CU.first += cost_vect_temp[0];
							// Tx_cost_CU.second += cost_vect_temp[1];
							// Tx_CAPEX_year_0_CU += cost_vect_temp[2];
							
							// if(DEBUG_PLACEMENT)
							//	LogFile << (int)cost_vect_temp[3] << " 100G and " << (int)cost_vect_temp[4] << " 300G" << endl;
						}

						// TODO: add weights based on path length
						SNR_sum += SNR_demand;
						

						if (SNR_demand < SNR_worst)
							SNR_worst = SNR_demand;


						if (DEBUG_PLACEMENT)
							LogFile << "Demand " << (*itrDemand) -> get_id() << " from " << (*itrDemand) -> getEndId1() << " to " << (*itrDemand) -> getEndId2() << " : SNR: " << SNR_demand << " P_rx: " << P_rx << " bitrate: " << max_possible_throughput(SNR_demand);

						// if feasible
						// if (SNR_demand > SNR_threshold_dB && P_rx >= -18)
						// {
						// 	if (DEBUG_PLACEMENT)
						// 		LogFile << " feasible" << endl;
						// }
						if((*itrDemand) ->getType() == 10)
						{
							if (SNR_demand > SNR_threshold_10G && P_rx >= -18)
							{
								if (DEBUG_PLACEMENT)
									LogFile << " feasible" << endl;
							}
							else
							{
								all_feasible_paths = false;

								if (DEBUG_PLACEMENT)
									LogFile << " unfeasible" << endl;

								// if we've reached feasibility, unfeasible solutions are of little interest
								if (!DEBUG_PLACEMENT and FULL_OPTIMIZATION && GenAmpPlacement.is_feasible())
									break;
							}
						}

						else if((*itrDemand) ->getType() == 100)
						{
							if (SNR_demand > SNR_threshold_100G && P_rx >= -18)
							{
								if (DEBUG_PLACEMENT)
									LogFile << " feasible" << endl;
							}
							else
							{
								all_feasible_paths = false;

								if (DEBUG_PLACEMENT)
									LogFile << " unfeasible" << endl;

								// if we've reached feasibility, unfeasible solutions are of little interest
								if (!DEBUG_PLACEMENT and FULL_OPTIMIZATION && GenAmpPlacement.is_feasible())
									break;
							}
						}	
						else if((*itrDemand) ->getType() == 200)
						{
							if (SNR_demand > SNR_threshold_200G && P_rx >= -18)
							{
								if (DEBUG_PLACEMENT)
									LogFile << " feasible" << endl;
							}
							else
							{
								all_feasible_paths = false;

								if (DEBUG_PLACEMENT)
									LogFile << " unfeasible" << endl;

								// if we've reached feasibility, unfeasible solutions are of little interest
								if (!DEBUG_PLACEMENT and FULL_OPTIMIZATION && GenAmpPlacement.is_feasible())
									break;
							}
						}

					}
					// cout << all_feasible_paths << endl;
					// cin.ignore();

					if(fast_run and all_feasible_paths == false)
						break;

					unique_feasibility_vect[GA_solution_ind] += all_feasible_paths;
				}
			}

			// find the ratio: 0 - 1
			unique_feasibility_vect[GA_solution_ind] /= final_lps.size();

			//LogFile << "Feasibility " << unique_feasibility_vect[GA_solution_ind] << endl;

			// validating that power at EDFAs computed during gain setting and SNR calculation is the same
			// in other words, validating that LOGO-optimal powers are enforced
			

			// if(unique_feasibility_vect[GA_solution_ind] == 1)
			// {
			// 	for(auto itrOAgain = OaLocationList.begin(); itrOAgain != OaLocationList.end(); itrOAgain++)
			// 	{
			// 		if((*itrOAgain) -> m_OaLocIndicator)
			// 		{
			// 			cout << "PLEAAAAASE! 2" << endl;
			// 			cin.ignore();
			// 			float min_val_g = 1e6;
			// 			float max_val_g = -1e6;

			// 			//LogFile << "EDFA " << (*itrOAgain) -> getOaId() << " mentioned " << power_at_EDFA_second[(*itrOAgain) -> getOaId()].size() << " and " << power_at_EDFA[(*itrOAgain) -> getOaId()].size() << " times" << endl;

			// 			for(auto itrP = power_at_EDFA_second[(*itrOAgain) -> getOaId()].begin(); itrP != power_at_EDFA_second[(*itrOAgain) -> getOaId()].end(); itrP ++)
			// 			{
			// 				if ( (*itrP) < min_val_g)
			// 					min_val_g = (*itrP);

			// 				if ( (*itrP) > max_val_g)
			// 					max_val_g = (*itrP);
			// 			}

			// 			/*if (abs(min_val_g - max_val_g) > 0.1)
			// 			{
			// 				cout << "Location " << (*itrOAgain) -> getOaId() << " on link " << (*itrOAgain) -> m_OaLocLink << " at " << (*itrOAgain) -> m_OaLocLength << " of type " << (*itrOAgain)->m_OaType << " with gain " << (*itrOAgain)->gain_dB << endl; 
			// 				for(auto itrP = power_at_EDFA_second[(*itrOAgain) -> getOaId()].begin(); itrP != power_at_EDFA_second[(*itrOAgain) -> getOaId()].end(); itrP ++)
			// 					cout << (*itrP) << " ";
			// 				cout << endl;

			// 				for(auto itrOA = OaLocationList.begin(); itrOA != OaLocationList.end(); itrOA++)
			// 					if((*itrOA) -> m_OaLocIndicator)
			// 						cout << (*itrOA)->getOaId() << "; ";
			// 				cout << endl;

			// 				//throw runtime_error("Power at EDFA is not consistent for different signals");
			// 			}*/

			// 			/*if (abs(min_val_g - power_at_EDFA[(*itrOAgain) -> getOaId()].back()) > 0.1)
			// 			{
			// 				cout << "Location " << (*itrOAgain) -> getOaId() << " on link " << (*itrOAgain) -> m_OaLocLink << " at " << (*itrOAgain) -> m_OaLocLength << " of type " << (*itrOAgain)->m_OaType << " with gain " << (*itrOAgain)->gain_dB << " and attenuation " << (*itrOAgain) -> att_dB << endl; 
			// 				for(auto itrP = power_at_EDFA[(*itrOAgain) -> getOaId()].begin(); itrP != power_at_EDFA[(*itrOAgain) -> getOaId()].end(); itrP ++)
			// 					cout << (*itrP) << " ";
			// 				cout << endl;

			// 				for(auto itrP = power_at_EDFA_second[(*itrOAgain) -> getOaId()].begin(); itrP != power_at_EDFA_second[(*itrOAgain) -> getOaId()].end(); itrP ++)
			// 					cout << (*itrP) << " ";
			// 				cout << endl;

			// 				for(auto itrOA = OaLocationList.begin(); itrOA != OaLocationList.end(); itrOA++)
			// 					if((*itrOA) -> m_OaLocIndicator)
			// 						cout << (*itrOA)->getOaId() << "; ";
			// 				cout << endl;

			// 				//throw runtime_error("Power at EDFA is different from when gain was set");
			// 			}*/

			// 			//LogFile << "3" << endl;

			// 			if(fabs(power_at_EDFA_second[(*itrOAgain) -> getOaId()].back() - (*itrOAgain) -> power_out_dBm) > 0.1)
			// 			{
			// 				cout << (*itrOAgain)->getOaId() << endl;
			// 				cout << (*itrOAgain) -> power_out_dBm << " vs " << power_at_EDFA_second[(*itrOAgain) -> getOaId()].back() << endl;
			// 				throw runtime_error("power_out_dBm is not consistent with power_at_EDFA_second");
			// 			}

			// 			if(fabs(power_at_EDFA[(*itrOAgain) -> getOaId()].back() - (*itrOAgain) -> power_out_dBm) > 0.1)
			// 			{
			// 				cout << (*itrOAgain)->getOaId() << endl;
			// 				cout << (*itrOAgain) -> power_out_dBm << " vs " << power_at_EDFA[(*itrOAgain) -> getOaId()].back() << endl;
			// 				throw runtime_error("power_out_dBm is not consistent with power_at_EDFA");
			// 			}

			// 			cout << "PLEAAAAASE! 3" << endl;
			// 			cin.ignore();

			// 			//LogFile << "4" << endl;
			// 		}
			// 	}
			// }
			// cout << "PLEAAAAASE! 4" << endl;
			// cin.ignore();

			//LogFile << "Power checks done" << endl;

			//OA_OSNR_file.close();


			// assign fitness values depending on the objective
			// double equip_cost = Tx_cost_CU.first + Tx_cost_CU.second + OA_cost_CU.first + OA_cost_CU.second + switch_cost_CU.first + switch_cost_CU.second;
			double equip_cost = OA_cost_CU.first + OA_cost_CU.second;

			if (OA_placement_objective == OA_Objective::COST)
			{
				unique_fitness_vect[GA_solution_ind] = equip_cost;
				unique_secondary_fitness_vect[GA_solution_ind] = -SNR_worst;
			}

			else if (OA_placement_objective == OA_Objective::MIN_SNR)
			{
				unique_fitness_vect[GA_solution_ind] = -SNR_worst;
				unique_secondary_fitness_vect[GA_solution_ind] = equip_cost;
			}

			else if(OA_placement_objective == OA_Objective::AV_SNR)
			{
				unique_fitness_vect[GA_solution_ind] = -SNR_sum / num_paths;
				unique_secondary_fitness_vect[GA_solution_ind] = -SNR_worst;
			}

			else if (OA_placement_objective == OA_Objective::TRAFFIC)
			{
				unique_fitness_vect[GA_solution_ind] = network_throughput_G;
				unique_secondary_fitness_vect[GA_solution_ind] = equip_cost;
			}

			else
				throw runtime_error("Unknown objective");

			// just the first solution is used
			if(baseline_mode and fast_run)
			{
				if (unique_feasibility_vect[0] == 1)
					return unique_fitness_vect[0];

				else
					return 1e6;
			}

			else if ((baseline_mode or DEBUG_PLACEMENT) and fast_run == false)
				break;
		}

		if ((baseline_mode or DEBUG_PLACEMENT) and fast_run == false)
			break;

		for (int sol_ind = 0; sol_ind < matching_list_solutions.size(); sol_ind ++)
        {
            fitness_matrix[0][sol_ind] = unique_fitness_vect[matching_list_solutions[sol_ind]];
            fitness_matrix[1][sol_ind] = unique_secondary_fitness_vect[matching_list_solutions[sol_ind]];
            feasibility_vect[sol_ind] = unique_feasibility_vect[matching_list_solutions[sol_ind]];

            if (feasibility_vect[sol_ind] == 1.0 && fitness_matrix[0][sol_ind] < best_cost)
			{
                best_cost = fitness_matrix[0][sol_ind];
			}
        }

		// next generation
		GenAmpPlacement.next_generation(feasibility_vect, fitness_matrix);
	}

	if (fast_run)
		return best_cost;
		
	else
	{
		// current date/time based on current system
		time_t now = time(0);

		LogFile << endl << endl << "***************************" << endl;
		LogFile << ctime(&now) << "***************************" << endl;
	}

	
	// get the best solutions
	if (baseline_mode == false and DEBUG_PLACEMENT == false)
		pop_size = GenAmpPlacement.set_best_solutions();
	
	//return best_cost;


	// for test network
	vector<int> bitrate_range_G_test = {0, 500};
	std::discrete_distribution<int> bitrate_dist_test = {0, 100};

	// for metro-aggregation networks
	vector<int> bitrate_range_G_metro = {0, 50, 100, 150};
	std::discrete_distribution<int> bitrate_dist_metro = {0, 33, 33, 34};

	// for metro-core networks
	vector<int> bitrate_range_G_metro_core = {0, 100, 150, 200};
	std::discrete_distribution<int> bitrate_dist_metro_core = {25, 25, 25, 25};

	// for core networks
	vector<int> bitrate_range_G_core = {0, 150, 200, 250};
	std::discrete_distribution<int> bitrate_dist_core = {50, 25, 25, 0};


	vector<double> OA_CAPEX_vect(pop_size, 0);
	vector<double> OA_OPEX_vect(pop_size, 0);
	vector<map<int, int>> EDFA_per_type_vect;

	vector<map<int, int>> Tx_per_type;

	vector<double> Tx_CAPEX_vect(pop_size, 0);
	vector<double> Tx_OPEX_vect(pop_size, 0);
	vector<double> Tx_CAPEX_0_vect(pop_size, 0);
	
	vector<double> cost_vect(pop_size, 0);
	vector<double> minSNR_vect(pop_size, 0);
	vector<double> avSNR_vect(pop_size, 0);
	vector<double> throughput_vect(pop_size, 0);
	vector<double> av_demand_vect(pop_size, 0);

	vector<int> WI_vect(pop_size, 0);
	vector<int> total_spectrum_occupation_vect(pop_size, 0);


	for (int GA_solution_ind = 0; GA_solution_ind < pop_size; GA_solution_ind ++)
	{
		for(int gene_ind = 0; gene_ind < OaLocationList.size(); gene_ind ++)
			OaLocationList[gene_ind] -> m_OaLocIndicator = (int)(GenAmpPlacement.is_selected_gene_active(GA_solution_ind, gene_ind));

		// set the gains
		bool gain_can_compensate_losses = gainOAfunc(LogFile);

		if (gain_can_compensate_losses == false)
			throw runtime_error("Unfeasible OA placement ended up as the best solution");

		pair<double, double> OA_cost_CU(0, 0);
		map<int, int> EDFA_per_type;
				
		for (auto itrLoc = OaLocationList.begin(); itrLoc != OaLocationList.end(); itrLoc ++)
		{
			if ((*itrLoc) -> m_OaLocIndicator == 1)
			{	
				if ((*itrLoc) -> gain_dB < 1)
					(*itrLoc) -> m_OaLocIndicator = 0;
				
				else
				{
					OA_cost_CU.first += (*itrLoc) -> m_OaCost;

					// electricity cost
					//if ( (*itrLoc) -> m_OaType == 1 or (*itrLoc) -> m_OaType == 2)
					OA_cost_CU.second += 0.008 * 0.001 * 24 * 365 * 5;

					//else if ( (*itrLoc) -> m_OaType == 3)
					//	OA_cost_CU.second += 0.018 * 0.001 * 24 * 365 * 5;

					EDFA_per_type[(*itrLoc) -> m_OaType] ++;
				}	
			}
		}

		// other costs
		OA_cost_CU.first *= 1.3;
		OA_cost_CU.second *= 1.75;

		OA_CAPEX_vect[GA_solution_ind] += OA_cost_CU.first;
		OA_OPEX_vect[GA_solution_ind] += OA_cost_CU.second;
		EDFA_per_type_vect.push_back(EDFA_per_type);


		map<int, int> Tx_type;

		int num_traffic_instances = 20;

		// traffic generation
		std::mt19937 random_generator;
		std::discrete_distribution<int> bitrate_dist;
		random_generator = std::mt19937(42); //dev()

		for (int traffic_instance = 0; traffic_instance < num_traffic_instances; traffic_instance ++)
		{
			vector<double> request_vect;

			for(auto itrDemand = final_lps.begin(); itrDemand != final_lps.end(); itrDemand++)
			{
				int traffic_request_G = 0;

				// if(getNumberOfNodes() == 4)
				// 	traffic_request_G = bitrate_range_G_test[bitrate_dist_test(random_generator)];
				
				// // core demands
				// else if ( (getNumberOfNodes() == 10 or getNumberOfNodes() == 17) and (*itrDemand)-> m_nChoice == 400)
				// 	traffic_request_G = bitrate_range_G_core[bitrate_dist_core(random_generator)];

				// // metro-core demands
				// else if  ( (getNumberOfNodes() == 8 or getNumberOfNodes() == 17) and (*itrDemand)-> m_nChoice == 300)
				// 	traffic_request_G = bitrate_range_G_metro_core[bitrate_dist_metro_core(random_generator)];
						
				// else // metro topo
				
				traffic_request_G = bitrate_range_G_metro[bitrate_dist_metro(random_generator)];

				request_vect.push_back(traffic_request_G);
			}


			vector<vector<bool>> channel_occupation;
			vector<bool> temp((int)this -> n_channels, 0);
			for(auto itrLink = uni_fibers.begin(); itrLink != uni_fibers.end(); itrLink ++)
				channel_occupation.push_back(temp);

			map<int, int> ch_occ;


			// pair<double, double> Tx_cost_CU(0, 0);
			// double Tx_CAPEX_year_0_CU = 0;
			
			double SNR_worst = 1000;
			double SNR_sum = 0;

			int throughput_G = 0;
			int total_request_G = 0;

			int lpth_counter = 0;

			// go through all the demands and calculate the OSNR
			for(auto itrDemand = final_lps.begin(); itrDemand != final_lps.end(); itrDemand++)
			{
				////LogFile << (*itrDemand) ->m_nSequenceNo << " request: " << request_vect[itrDemand - allDemands.begin()] << " G" << endl;

				if (request_vect[itrDemand - final_lps.begin()] == 0)
					continue;

				bool resources_allocated = false;
				
				// first path - SNR - n. of channels - spectrum occupation
				// if not enough spectrum - second path - SNR - n. of channels - spectrum occupation
				for(auto itrPath = (*itrDemand)->candidate_paths.begin(); itrPath != (*itrDemand)->candidate_paths.end(); itrPath ++)
				{
					////LogFile << "Path " << itrPath - (*itrDemand)->candidate_paths.begin() << " out of " << (*itrDemand)->candidate_paths.size() << endl;

					pair<double, double> temp = calculateDemandSNR(LogFile, *itrPath, (*itrDemand)->getType());
					double SNR_demand = temp.first;
				
					int max_traffic_G = max_possible_throughput(SNR_demand);

					if (max_traffic_G == 0)
						continue;

					vector<int> avail_bitrate_G(2, 0);

					if(max_traffic_G >= 100)
						avail_bitrate_G[0] = 100;
							
					avail_bitrate_G[1] = max_traffic_G;		
					

					int traffic_request_G = request_vect[itrDemand - final_lps.begin()];
					vector<double> cost_vect_temp = {1.0, 1.0, 1.0, 1.0, 1.0};// ILP_Tx(traffic_request_G, avail_bitrate_G, {5, 12}, 5, 0.2, Tx_ILP_mutex, Tx_ILP_cache);

					int channels_to_allocate = cost_vect_temp[3] + cost_vect_temp[4];

					////LogFile << "Trying to allocate " << channels_to_allocate << " channels" << endl;

					if (filterless)
					{
						resources_allocated = true;

						for(auto itrLink = uni_fibers.begin(); itrLink != uni_fibers.end(); itrLink ++)
						{
							if (ch_occ[(*itrLink)->getId()] + channels_to_allocate > n_channels)
							{
								resources_allocated = false;
								break;
							}
						}

						if (resources_allocated)
						{
							for(auto itrLink = uni_fibers.begin(); itrLink != uni_fibers.end(); itrLink ++)
								ch_occ[(*itrLink)->getId()] += channels_to_allocate;
						}

						else
							break;
					}

					else if (filterless == false or blockers == true)
					{
						int first_channel = 0; 

						for(first_channel = 0; first_channel < n_channels - channels_to_allocate + 1; first_channel ++)
						{
							resources_allocated = true;

							for(auto itrLink = (*itrPath).begin(); itrLink != (*itrPath).end(); itrLink ++)
							{
								for (int ch_ind = 0; ch_ind < channels_to_allocate; ch_ind ++)
								{
									if (channel_occupation[(*itrLink) -> getId()][first_channel + ch_ind])
									{
										resources_allocated = false;
										break;
									}
								}

								if (resources_allocated == false)
									break;
							}
							
							if (resources_allocated)
								break;
						}

						if(resources_allocated)
						{
							////LogFile << "First available channel: " << first_channel << endl;

							for(auto itrLink = (*itrPath).begin(); itrLink != (*itrPath).end(); itrLink ++)
							{
								for (int ch_ind = 0; ch_ind < channels_to_allocate; ch_ind ++)
									channel_occupation[(*itrLink) -> getId()][first_channel + ch_ind] = 1;

								ch_occ[(*itrLink) -> getId()] += channels_to_allocate;
							}
						}

						else
							continue;
					}

	
					// Tx_cost_CU.first += cost_vect_temp[0];
					// Tx_cost_CU.second += cost_vect_temp[1];

					// Tx_CAPEX_year_0_CU += cost_vect_temp[2];

					// Tx_type[100] += cost_vect_temp[3];
					// Tx_type[300] += cost_vect_temp[4];


					////LogFile << "Demand " << (*itrDemand) ->m_nSequenceNo - 1 << " must carry " << (*itrDemand) -> m_nChoice << " can carry " << max_traffic_G << "G using " << cost_vect_temp[3] << " 100G and " << cost_vect_temp[4] << " 300G" << endl; 
					////LogFile << Tx_type[100] << " " << Tx_type[300] << endl;

					// TODO: add weights
					SNR_sum += SNR_demand;

					if (SNR_demand < SNR_worst)
						SNR_worst = SNR_demand;

					throughput_G += avail_bitrate_G[0] * cost_vect_temp[3] + avail_bitrate_G[1] * cost_vect_temp[4];						
					total_request_G += traffic_request_G * pow(1 + 0.2, 4);
					request_vect[itrDemand - final_lps.begin()] = 0;
					
					lpth_counter ++;

					break;
				}

				// if (resources_allocated == false)
				// 	throw runtime_error("Resources cannot be allocated");
			}

			// if (total_request_G == 0)
			// 	throw runtime_error("All request are 0");

			// Tx_CAPEX_vect[GA_solution_ind] += Tx_cost_CU.first;
			// Tx_CAPEX_0_vect[GA_solution_ind] += Tx_CAPEX_year_0_CU;
			// Tx_OPEX_vect[GA_solution_ind] += Tx_cost_CU.second;	
			// cost_vect[GA_solution_ind] += (Tx_cost_CU.first + Tx_cost_CU.second + OA_cost_CU.first + OA_cost_CU.second + switch_cost_CU.first + switch_cost_CU.second);
			cost_vect[GA_solution_ind] += (OA_cost_CU.first + OA_cost_CU.second);

			avSNR_vect[GA_solution_ind] += (-SNR_sum / lpth_counter);
			minSNR_vect[GA_solution_ind] += (-SNR_worst);
			throughput_vect[GA_solution_ind] += (-throughput_G);
			av_demand_vect[GA_solution_ind] += total_request_G;

			int total_channels = 0;
			int WI = 0;

			for(auto itrLink = uni_fibers.begin(); itrLink != uni_fibers.end(); itrLink ++)
			{
				for(int ch_ind = 0; ch_ind < (int)this -> n_channels; ch_ind ++)
					if (channel_occupation[(*itrLink) -> getId()][ch_ind] and ch_ind > WI)
						WI = ch_ind;

				total_channels += ch_occ[(*itrLink) -> getId()];
			}

			WI_vect[GA_solution_ind] += WI;
			total_spectrum_occupation_vect[GA_solution_ind] += total_channels;
		}

		Tx_CAPEX_vect[GA_solution_ind] /= num_traffic_instances;
		Tx_CAPEX_0_vect[GA_solution_ind] /= num_traffic_instances;
		Tx_OPEX_vect[GA_solution_ind] /= num_traffic_instances;
		cost_vect[GA_solution_ind] /= num_traffic_instances;

		Tx_type[100] /= num_traffic_instances;
		Tx_type[300] /= num_traffic_instances;
		Tx_per_type.push_back(Tx_type);

		avSNR_vect[GA_solution_ind] /= num_traffic_instances;
		minSNR_vect[GA_solution_ind] /= num_traffic_instances;
		throughput_vect[GA_solution_ind] /= num_traffic_instances;
		av_demand_vect[GA_solution_ind] /= num_traffic_instances;

		total_spectrum_occupation_vect[GA_solution_ind] /= num_traffic_instances;
		WI_vect[GA_solution_ind] /= num_traffic_instances;
	}

	vector<double> first_obj;
	vector<double> second_obj;
	vector<double> third_obj;

	if(OA_placement_objective == OA_Objective::COST)
	{
		first_obj = cost_vect;
		// second_obj = minSNR_vect;
		// third_obj = avSNR_vect;
		second_obj = avSNR_vect;
		third_obj = minSNR_vect;
	}

	else if(OA_placement_objective == OA_Objective::TRAFFIC)
	{
		first_obj = throughput_vect;
		second_obj = cost_vect;
		third_obj = avSNR_vect;
	}
			
	else if (OA_placement_objective == OA_Objective::MIN_SNR)
	{
		first_obj = minSNR_vect;
		second_obj = cost_vect;
		third_obj = avSNR_vect;
	}

	else if (OA_placement_objective == OA_Objective::AV_SNR)
	{
		first_obj = avSNR_vect;
		second_obj = cost_vect;//minSNR_vect;
		third_obj = minSNR_vect;//cost_vect;
	}

	vector<int> sorted_ind(cost_vect.size());
	for(int i = 0; i < sorted_ind.size(); i ++)
		sorted_ind[i] = i;

	std::sort(sorted_ind.begin(), sorted_ind.end(), [&] (int one, int two)
	{
		if ( abs(first_obj[one] - first_obj[two]) > 1e-6)
			return first_obj[one] < first_obj[two];

		if ( abs(second_obj[one] - second_obj[two]) > 1e-6)
			return second_obj[one] > second_obj[two];

		return third_obj[one] > third_obj[two];
	} );

	
	if(sorted_ind.size() != 0)
		LogFile << "Best solution is " << sorted_ind[0] << endl; 

	if(GenAmpPlacement.is_feasible())
		best_cost = first_obj[sorted_ind[0]];

	int number_of_print = 100;
	if (sorted_ind.size() <= number_of_print)
	{
		number_of_print = sorted_ind.size();
	}
	double SNR_avg_200 = 0;
	int m = 0;
	// go through all the best solutions
	for (int i = 0; i < number_of_print; i++)
	{
		LogFile << "SOLUTION " << i << " " << sorted_ind[i] << endl;
		LogFile << "Genes placed: ";

		GenAmpPlacement.print_solution(sorted_ind[i], LogFile, 0);
		LogFile << endl;

		// LogFile << "Tx CAPEX Year 0: " << Tx_CAPEX_0_vect[sorted_ind[i]] << endl;
		// LogFile << "Tx CAPEX: " << Tx_CAPEX_vect[sorted_ind[i]] << endl;
		// LogFile << "Tx OPEX: " << Tx_OPEX_vect[sorted_ind[i]] << endl;	
		LogFile << "OA CAPEX: " << OA_CAPEX_vect[sorted_ind[i]] << endl;
		LogFile << "OA OPEX: " << OA_OPEX_vect[sorted_ind[i]] << endl;	
		// LogFile << "Switching CAPEX: " << switch_cost_CU.first << endl;
		// LogFile << "Switching OPEX: " << switch_cost_CU.second << endl;
		LogFile << "Total cost: " << cost_vect[sorted_ind[i]] << endl << endl; 
		LogFile << "SNR average: " << -avSNR_vect[sorted_ind[i]] << " dB" << endl;
		LogFile << "SNR_worst: " << -minSNR_vect[sorted_ind[i]] << " dB" << endl;
		for (auto n = final_lps.begin(); n != final_lps.end(); n++)
		{
			if ((*n)->getType() == 200)
			{
				SNR_avg_200 += avSNR_vect[sorted_ind[i]];
				m ++;
			}

			// for(auto itrPath1 = (*n)->candidate_paths.begin(); itrPath1 != (*n)->candidate_paths.end(); itrPath1 ++)
			// {
			// 	pair<double, double> temp = calculateDemandSNR(OA_OSNR_file, *itrPath1, (*n)->getType());
				
			// 	double SNR_demand = temp.first;
			// 	cout << "LP" << k <<" with SNR " <<SNR_demand << endl;
				
			// }
			// k++;
		}	
		LogFile << "SNR average 200: " << SNR_avg_200 / m << " dB" << endl;
		// for(int i = 0 ; i < lp_SNR.size(); i++)
		// {
		// 	cout << lp_SNR[i] << endl;
		// }

		// LogFile << "Request: " <<  av_demand_vect[sorted_ind[i]] << " G" << endl;
		// LogFile << "Throughput: " << -throughput_vect[sorted_ind[i]] << " G" << endl;

		// LogFile << "Highest occupied channel: " << WI_vect[sorted_ind[i]] << endl;
		// LogFile << "Total spectrum occupation: " << total_spectrum_occupation_vect[sorted_ind[i]] << endl;
				
		// LogFile << "EDFA types" << endl;
		// for(auto map_itr = EDFA_per_type_vect[sorted_ind[i]].begin(); map_itr != EDFA_per_type_vect[sorted_ind[i]].end(); map_itr ++)
		// 	LogFile << map_itr->first << " : " << map_itr->second << endl;

		// LogFile << "TRX types" << endl;
		// for(auto map_itr = Tx_per_type[sorted_ind[i]].begin(); map_itr != Tx_per_type[sorted_ind[i]].end(); map_itr ++)
		// 	LogFile << map_itr->first << " : " << map_itr->second << endl;

		LogFile << "**************************************************************" << endl << endl;
	}
	int k = 0;
	for (auto n = final_lps.begin(); n != final_lps.end(); n++)
	{
		for(auto itrPath1 = (*n)->candidate_paths.begin(); itrPath1 != (*n)->candidate_paths.end(); itrPath1 ++)
		{
			pair<double, double> temp = calculateDemandSNR(OA_OSNR_file, *itrPath1, (*n)->getType());
			
			double SNR_demand = temp.first;
			cout << "LP" << k <<" with SNR " <<SNR_demand << endl;
			
		}
		k++;
	}

	return best_cost;
}

pair<double, double> Network :: calculateDemandSNR(ofstream& LogFile, vector<Unifiber*>& path, int lp_type)
{
	// 26 dB TRX SNR
	double NSR_Tx_lin = 1 / pow(10, 26 / 10);

	// distance from the start of the link to the beginning of the current span
	int previous_location_at_link_km = 0;

	// distance from the previous location to the end of the link
	int temp_length_till_link_end_km = 0;
	float span_loss_dB = 0;

	double propagated_NSR_lin = 0; 		// for the filterless case	
	double total_NSR_lin = 0; 			// total NSR in linear units

	bool first_span = true;
	bool last_span = false;

	int prev_link_id = -1;


	bool SNR_below_threshold = false;

	// 1 dBm at the transponder output
	double current_power_dBm = 1;

	if (path.size() == 0)
		throw runtime_error("Path length 0");

	// go through all the links of our demand
	for(auto linkItr = path.begin(); linkItr != path.end(); linkItr ++)
	{
		Unifiber* current_link = *linkItr;
		Node* src_node = current_link -> src_node;
		
		if(QOT_DEBUG_OUTPUT)
			LogFile << endl << "SNR calculation at link " << current_link -> getId() << endl;
		//cout << endl << "SNR calculation at link " << current_link -> getId() << endl;	
		bool first_loc_on_link = true;
		previous_location_at_link_km = 0;
				
		// first node: 6 dB multiplexor loss + output loss
		if (linkItr == path.begin())
        {
			span_loss_dB += filter_loss_dB;
            current_power_dBm -= filter_loss_dB;

			if(QOT_DEBUG_OUTPUT)
				LogFile << "Power after " << filter_loss_dB << "dB filter loss: " << current_power_dBm << endl  << "Span loss after " << filter_loss_dB << "dB filter loss: " << span_loss_dB << endl;
		}
				
		else
		{
            // input port loss
			float in_power_loss_dB = connector_loss_dB + current_link -> src_node -> port_loss_dB[current_link -> getId()];
            span_loss_dB += in_power_loss_dB;
            current_power_dBm -= in_power_loss_dB;

			if(QOT_DEBUG_OUTPUT)
				LogFile << "Power after " << in_power_loss_dB << "dB in loss: " << current_power_dBm  << endl << "Span loss after " << in_power_loss_dB << "dB in loss: " << span_loss_dB << endl;
        }


		// equalization: difference between the current power and the lowest power signal passing through the node
		float eq_loss_dB = current_power_dBm - src_node -> lowest_power_dBm_per_output_link[current_link -> getId()];
           
        span_loss_dB += eq_loss_dB;
        current_power_dBm -= eq_loss_dB;

		if(QOT_DEBUG_OUTPUT)
		{
			LogFile << "Minimum power: " << src_node -> lowest_power_dBm_per_output_link[current_link -> getId()] << endl;
			LogFile << "Power after " << eq_loss_dB << "dB eq loss: " << current_power_dBm << endl << "Span loss after " << eq_loss_dB << "dB eq loss: " << span_loss_dB << endl;
		}

		float out_power_loss_dB = current_link -> src_node -> port_loss_dB[current_link -> getId()] + connector_loss_dB;
		span_loss_dB += out_power_loss_dB;
        current_power_dBm -= out_power_loss_dB;

		if(QOT_DEBUG_OUTPUT)
			LogFile << "Power after " << out_power_loss_dB << "dB out loss: " << current_power_dBm << endl << "Span loss after " << out_power_loss_dB << "dB out loss: " << span_loss_dB << endl;


		for (auto itrLoc = temp_link_EDFAs_map[current_link -> getId()].begin(); itrLoc != temp_link_EDFAs_map[current_link -> getId()].end(); itrLoc ++)
		{
			OaLoc* current_EDFA = *itrLoc;

			if(current_EDFA -> m_OaLocIndicator != 1)
				throw runtime_error("Smth is very wrong with the saved EDFA");

			if(QOT_DEBUG_OUTPUT)
				LogFile << endl << "OA: " << current_EDFA -> m_OaLocId << " at " << current_EDFA -> m_OaLocLength << endl;
				
			// span length, including only fiber at the current link
			int span_length_km = current_EDFA -> m_OaLocLength - previous_location_at_link_km;
			previous_location_at_link_km = current_EDFA -> m_OaLocLength;

			if(QOT_DEBUG_OUTPUT)
				LogFile << span_length_km << " km long span" << endl;

			float prop_loss_dB = span_length_km * att_coeff_dB_km;
			span_loss_dB += prop_loss_dB;
			current_power_dBm -= prop_loss_dB;

			if(QOT_DEBUG_OUTPUT)
				LogFile << "Power after " << prop_loss_dB << "dB prop loss: " << current_power_dBm << endl << "Span loss after " << prop_loss_dB << "dB prop loss: " << span_loss_dB << endl;

			// connector at the end of the span (before the EDFA)
			if(current_EDFA -> m_OaType != 1)
			{
				span_loss_dB += connector_loss_dB;
				current_power_dBm -= connector_loss_dB;
				
				if(QOT_DEBUG_OUTPUT)
					LogFile << "Power after " << connector_loss_dB << "dB con loss: " << current_power_dBm << endl  << "Span loss after " << connector_loss_dB << "dB con loss: " << span_loss_dB << endl;
			}


			int first_subspan_length_km = span_length_km;

			// if it's a trans-node span, don't consider the fiber after the node
			if (first_loc_on_link == true)
				first_subspan_length_km = temp_length_till_link_end_km;
			
			temp_length_till_link_end_km = current_link -> getLength() - current_EDFA -> m_OaLocLength;

			if(QOT_DEBUG_OUTPUT)
				LogFile << temp_length_till_link_end_km << " of fiber before the node" << endl;

			// if it's the last link and preamp is placed
			if (linkItr == path.end() - 1 && current_link -> getLength() == current_EDFA -> m_OaLocLength)
				last_span = true;

			// we assume that the loss is always compensated by the gain
			// as the lower OA gain is fixed - attenuator has to be added at the end of the span if it's too short
			if(current_EDFA -> att_dB > 0)
			{
				span_loss_dB += current_EDFA -> att_dB;
				current_power_dBm -= current_EDFA -> att_dB;

				if(QOT_DEBUG_OUTPUT)
					LogFile << "Power after " << current_EDFA -> att_dB << "dB att loss: " << current_power_dBm << endl << "Span loss after " << current_EDFA -> att_dB << "dB att loss: " << span_loss_dB << endl;
			}
			
			current_power_dBm += current_EDFA -> gain_dB;

			if(QOT_DEBUG_OUTPUT)
				LogFile << "Power after " << current_EDFA -> gain_dB << "dB gain: " << current_power_dBm << endl;

			power_at_EDFA_second[current_EDFA -> getOaId()].push_back(current_power_dBm);
 
			// account for the propagated OSNR at the beginning of each link
			if (filterless and first_loc_on_link and (first_span or current_link -> src_node -> inDegree() > 2))
			{
				////LogFile << endl << "Initial propagation as if it's the first span of the demand" << endl;
				set<int>visited_links;
				pair<double, bool> temp_NSR = calculatePropagatedSNR(current_EDFA, true, visited_links);
							
				// first track the noise from all directions to this OA
				if(first_span)
					propagated_NSR_lin = temp_NSR.first;

				// if node degree is more than 2, select the noise from the required directions
				else if (current_link -> src_node -> inDegree() > 2)
				{
					////LogFile << endl << "Retrieving propagated ASE from links apart from " << prev_link_id << endl;
					propagated_NSR_lin += current_EDFA -> m_AccumulatedOSNRperLink[prev_link_id];
				}
			}
			

			// pair of SNR and Power of the span
			pair<double, double> temp_QoT;

			// OSNR for this span has been computed already
			if (current_EDFA -> m_SNR_saved == true)
			{
				temp_QoT.first = current_EDFA -> m_span_SNR;
					
				if(QOT_DEBUG_OUTPUT)
					LogFile << "OSNR and power for this span are reused: " << 10 * log10(1/temp_QoT.first) << " dB; " << temp_QoT.second << endl;
			}

			// OSNR for this span has not been computed
			else
			{
				temp_QoT = spanSNR(first_subspan_length_km, current_power_dBm, false, current_EDFA);

				// we've stayed at the same link as the previous OA (not the trans-node span)
				// and this location doesn't start the demand
				// means that we can save this values and reuse them for another demand
				if (current_EDFA -> m_OaLocLink == prev_link_id)
				{
					current_EDFA -> m_SNR_saved = true;
					current_EDFA -> m_span_SNR = temp_QoT.first;

					if(QOT_DEBUG_OUTPUT)
						LogFile << "OSNR and power for this span are saved: " << 10 * log10(1/temp_QoT.first) << " dB; " << temp_QoT.second << endl;
				}
			}

			total_NSR_lin += temp_QoT.first;

			if(QOT_DEBUG_OUTPUT)
				LogFile << "Current SNR " << 10 * log10(1 / total_NSR_lin) << " dB " << temp_QoT.second << " dBm  power" << endl;

							
			// if the demand OSNR is below the threshold, it won't improve anymore
			// if(FULL_OPTIMIZATION && 10 * log10(1 / total_NSR_lin) < SNR_threshold_dB)
			// {
			// 	if(QOT_DEBUG_OUTPUT)
			// 		LogFile << "SNR is below the " << SNR_threshold_dB << " dB threshold" << endl; 
				
			// 	SNR_below_threshold = true;
			// 	break;
			// }
			if(FULL_OPTIMIZATION && lp_type == 10 && 10 * log10(1 / total_NSR_lin) < SNR_threshold_10G)
			{
				if(QOT_DEBUG_OUTPUT)
					LogFile << "SNR is below the " << SNR_threshold_10G << " dB threshold" << endl;

				SNR_below_threshold = true;
				break;
			}

			else if(FULL_OPTIMIZATION && lp_type == 100 && 10 * log10(1 / total_NSR_lin) < SNR_threshold_100G)
			{
				if(QOT_DEBUG_OUTPUT)
					LogFile << "SNR is below the " << SNR_threshold_100G << " dB threshold" << endl; 

				SNR_below_threshold = true;
				break;
			}	
			else if(FULL_OPTIMIZATION && lp_type == 200 && 10 * log10(1 / total_NSR_lin) < SNR_threshold_200G)
			{
				if(QOT_DEBUG_OUTPUT)
					LogFile << "SNR is below the " << SNR_threshold_200G << " dB threshold" << endl; 

				SNR_below_threshold = true;
				break;
			}

			first_span = false;
			first_loc_on_link = false;
			prev_link_id = current_EDFA -> m_OaLocLink;
			span_loss_dB = 0;

			if(last_span)
			{
				// 6 dB loss at the demultiplexer and an input port loss
				float drop_loss_dB = connector_loss_dB + current_link -> dst_node -> port_loss_dB[current_link -> getId()] + filter_loss_dB;

				current_power_dBm -= drop_loss_dB;
				
				if(QOT_DEBUG_OUTPUT)
					LogFile << "Power after " << drop_loss_dB << "dB drop loss: " << current_power_dBm << endl;

				break;
			}

			if(current_EDFA -> m_OaType != 3)
			{
				// connector after the EDFA
				span_loss_dB += connector_loss_dB;
				current_power_dBm -= connector_loss_dB;
				
				if(QOT_DEBUG_OUTPUT)
					LogFile << "Power after " << connector_loss_dB << "dB con loss: " << current_power_dBm << endl << "Span loss after " << connector_loss_dB << "dB con loss: " << span_loss_dB << endl;
			}
		}

		// if SNR is too low 
		if(last_span or SNR_below_threshold)
			break;

		// if it's the last link and there is no preamp
		if (linkItr == path.end() - 1)
		{
			// fetch the last OA location at that link
			OaLoc* last_location = temp_preamp_per_link_map[current_link -> getId()];
			
			if (last_location -> m_OaLocIndicator == 1)
				throw runtime_error("Smth is very wrong with last link without a preamp");
            
			if(QOT_DEBUG_OUTPUT)
				LogFile << endl << "Last span without a preamp: " << endl;

			// span length
			int span_length_km = last_location -> m_OaLocLength - previous_location_at_link_km;

			if(QOT_DEBUG_OUTPUT)
				LogFile << "Span length " << span_length_km << " km" << endl;
			
			if (first_span)
				temp_length_till_link_end_km = span_length_km;

			float prop_loss_dB = span_length_km * att_coeff_dB_km;
			float drop_loss_dB = current_link -> dst_node -> port_loss_dB[current_link -> getId()] + filter_loss_dB;

			float last_span_loss_dB = prop_loss_dB + connector_loss_dB + drop_loss_dB;
			span_loss_dB += last_span_loss_dB;
			
			// account for the propagated OSNR
			if (filterless and first_loc_on_link and (first_span or current_link -> src_node -> inDegree() > 2) )
			{
				////LogFile << endl << "Initial propagation as if it's the first span of the demand" << endl;

				OaLoc* first_location = temp_booster_per_link_map[current_link -> getId()];
				set<int>visited_links;
				pair<double, bool> temp_NSR = calculatePropagatedSNR(first_location, true, visited_links);
				// first track the noise from all directions to this OA
				if(first_span)
					propagated_NSR_lin = temp_NSR.first;

				// if node degree is more than 2, select the noise from the required directions
				else if (current_link -> src_node -> inDegree() > 2)
				{
					////LogFile << endl << "Retrieving propagated ASE from links apart from " << prev_link_id << endl;
					propagated_NSR_lin += first_location -> m_AccumulatedOSNRperLink[prev_link_id];
				}
			}

			first_loc_on_link = false;
			first_span = false;
			last_span = true;

			pair<double, double> temp = spanSNR(temp_length_till_link_end_km, current_power_dBm, true, last_location);

			total_NSR_lin += temp.first;

			current_power_dBm -= last_span_loss_dB;
			
			if(QOT_DEBUG_OUTPUT)
				LogFile << "Power after " << last_span_loss_dB << "dB span loss: " << current_power_dBm << endl << "Span loss after " << last_span_loss_dB << "dB span loss: " << span_loss_dB << endl;

			break;
		}

		// no EDFAs have been found on the link
		if(first_loc_on_link)
		{
			float prop_loss_dB = current_link -> getLength() * att_coeff_dB_km;
			span_loss_dB += prop_loss_dB;
        	current_power_dBm -= prop_loss_dB;

			if (QOT_DEBUG_OUTPUT)
				LogFile << "Power after the prop loss of the empty link: " << current_power_dBm << endl << "Span loss after the prop loss of the empty link: " << span_loss_dB << endl;
		}

		// end of the link after the EDFA
		else if (temp_length_till_link_end_km != 0)
		{
			float prop_loss_dB = temp_length_till_link_end_km * att_coeff_dB_km;
			span_loss_dB += prop_loss_dB;
            current_power_dBm -= prop_loss_dB;

			if (QOT_DEBUG_OUTPUT)
				LogFile << "Power after the prop loss of the link end: " << current_power_dBm << endl << "Span loss after the prop loss of the link end: " << span_loss_dB << endl;
		}
		
	}

	if (last_span != true and SNR_below_threshold == false)
		throw runtime_error("Last span never reached");

	total_NSR_lin += propagated_NSR_lin;

	double snr_dB = 10 * log10(1 / (total_NSR_lin + NSR_Tx_lin) );

	if(QOT_DEBUG_OUTPUT)
		LogFile << "Final SNR " << snr_dB << endl << "Final power: " << current_power_dBm << endl;

	return {snr_dB, current_power_dBm};
}

// ************************************************************************************************************************
// gainOAfunc
// calculates the gain of OAs while compensating for the highest loss
// and difference in launched powers in the succesive spans
bool Network :: gainOAfunc(ofstream& LogFile)
{
    const float TRX_power_dBm = 1;

	double alpha_linear = att_coeff_dB_km / (10 * log10(exp(1))) / 1e3;

	double log_func = log(pow(PI, 2) * abs(beta2) * pow(Rs_baud, 2) * pow(n_channels, 2 * Rs_baud / spacing_Hz) / alpha_linear);
    double constant_nli = (8.0 / 27.0) * alpha_linear * pow(gamma, 2) * log_func / (PI * abs(beta2) * pow(Rs_baud, 2));


	power_at_EDFA_second.clear();

	temp_preamp_per_link_map.clear();
	temp_booster_per_link_map.clear();

	for(auto itrOA = OaLocationList.begin(); itrOA != OaLocationList.end(); itrOA++)
	{
		(*itrOA) -> reset(lookUpLinkById((*itrOA) -> m_OaLocLink));
		(*itrOA) -> m_AccumulatedOSNRperLink.clear();

		if ( (*itrOA) -> m_OaType == 1)
		{
			temp_booster_per_link_map[(*itrOA) -> m_OaLocLink] = *itrOA;
		}

		else if ( (*itrOA) -> m_OaType == 3)
		{
			temp_preamp_per_link_map[(*itrOA) -> m_OaLocLink] = *itrOA;
		}
	}

	if(filterless)
	{
		// go through all the links
		for(auto itrLink = uni_fibers.begin(); itrLink != uni_fibers.end(); itrLink ++)
		{
			// find a first active location at the link
			for(auto itrLoc = OaLocationList.begin(); itrLoc != OaLocationList.end(); itrLoc ++)
			{
				if ((*itrLoc) -> m_OaLocIndicator && (*itrLoc) -> m_OaLocLink == (*itrLink) -> getId() )
				{
					// add the incoming links, apart from the opposite one to this link
					for(auto itrInLink = uni_fibers.begin(); itrInLink != uni_fibers.end(); itrInLink ++)
						if((*itrLink) -> src_node -> getID() == (*itrInLink) -> dst_node -> getID() and isOppositeLink(*itrInLink, *itrLink) == false)
							(*itrLoc) -> m_AccumulatedOSNRperLink[(*itrInLink) -> getId()] = 0;
					break;
				}
			}
		}
	}

	// reset lowest power in the node to the power of the added signal (for equalization)
	for(auto itrNode = nodes.begin(); itrNode != nodes.end(); itrNode ++)
	{
		(*itrNode) -> lowest_power_updated = false;
		(*itrNode) -> lowest_power_dBm_per_output_link.clear();

		for(auto itrLink = uni_fibers.begin(); itrLink != uni_fibers.end(); itrLink ++)
			if ( (*itrLink) -> src_node -> getID() == (*itrNode) -> getID() )
				(*itrNode) -> lowest_power_dBm_per_output_link[(*itrLink) -> getId()] = TRX_power_dBm - filter_loss_dB;
	}


	int iteration = 0;

	while(true)
	{
		temp_link_EDFAs_map.clear();
		power_at_EDFA.clear();

		// go through all the demands as the next demand may require a larger gain of a specific amplifier
		for(auto itrDemand = final_lps.begin(); itrDemand != final_lps.end(); itrDemand ++)
		{
			for(auto itrPath = (*itrDemand)->candidate_paths.begin(); itrPath != (*itrDemand)->candidate_paths.end(); itrPath ++)
			{
				if ((*itrPath).size() == 0)
					throw runtime_error("Path with no links");

				float current_power_dBm = TRX_power_dBm;
				
				// distance from the start of the link to the beginning of the current span
				int previous_location_at_link_km = 0;
				float span_loss_dB = 0;

				// distance from the last encounter EDFA till the end of the link
				int temp_length_till_link_end_km = 0;
					
				bool last_span = false;
				Unifiber* prev_link = nullptr;
				
				if (QOT_DEBUG_OUTPUT)
					LogFile << endl << endl << "Demand " << (*itrDemand) -> get_id() << " from " << (*itrDemand) -> getEndId1() << " to " << (*itrDemand) -> getEndId2() << endl;

				for(auto itrLink = (*itrPath).begin(); itrLink != (*itrPath).end(); itrLink ++)
				{
					Unifiber* current_link = *itrLink;
					Node* src_node = current_link -> src_node;

					bool first_loc_on_link = true;
					previous_location_at_link_km = 0;

					if (QOT_DEBUG_OUTPUT)
					{
						LogFile << "Link " << current_link -> getId() << endl;
						LogFile << "Node " << src_node->getID() << " degree " << src_node -> outDegree() << endl;
						LogFile << "Input loss " << src_node -> port_loss_dB[current_link->getId()] << endl;
					}

					// source node: multiplexer loss
					if (itrLink == (*itrPath).begin())
					{
						span_loss_dB += filter_loss_dB;
						current_power_dBm -= filter_loss_dB;

						if (QOT_DEBUG_OUTPUT)
							LogFile << "Power after the filter loss: " << current_power_dBm << endl << "Span loss after the filter loss: " << span_loss_dB << endl;
					}
					
					// passing through a node
					else
					{
						if(prev_link == nullptr)
							throw runtime_error("Previous link unknown");

						// connector at input port and input port loss
						float in_power_loss_dB = connector_loss_dB + src_node -> port_loss_dB[prev_link -> getId()];
						span_loss_dB += in_power_loss_dB;
						current_power_dBm -= in_power_loss_dB;
						
						if (QOT_DEBUG_OUTPUT)
							LogFile << "Power after the input loss: " << current_power_dBm << endl << "Span loss after the input loss: " << span_loss_dB << endl;
					}
						
					// equalization: difference between the current power and the lowest power signal passing out of the same port
					float eq_loss_dB = current_power_dBm - src_node -> lowest_power_dBm_per_output_link[current_link -> getId()];
					
					if (QOT_DEBUG_OUTPUT)
						LogFile << "Minimum power at the port of node " << src_node->getID() << " is " << src_node -> lowest_power_dBm_per_output_link[current_link -> getId()] << " Eq loss is " << eq_loss_dB << endl;

					if (eq_loss_dB < 0)
					{
						if(filterless)
						{
							if(fabs(eq_loss_dB) > 0.1)
								src_node -> lowest_power_updated = true;

							if(prev_link == nullptr)
								throw runtime_error("Minimum power shouldn't be updated at the src node");

							int opp_link_id = getOppositeLinkId(prev_link);

							// update lowest power at all output ports where the signal propagates
							for(auto itrEq = src_node -> lowest_power_dBm_per_output_link.begin(); itrEq != src_node -> lowest_power_dBm_per_output_link.end(); itrEq ++)
							{
								if(itrEq -> first != opp_link_id and current_power_dBm < itrEq -> second)
								{
									itrEq -> second = current_power_dBm;

									if (QOT_DEBUG_OUTPUT)
										LogFile << "New minimum power at the port of node " << src_node->getID() << " to link " << itrEq -> first << " is " << current_power_dBm << endl;
								}
							}
						}

						else
							src_node -> lowest_power_dBm_per_output_link[current_link -> getId()] = current_power_dBm;

						eq_loss_dB = 0;
						
						if (QOT_DEBUG_OUTPUT)
							LogFile << "New minimum power in node " << src_node->getID() << " is " << current_power_dBm << endl;
					}
						
					span_loss_dB += eq_loss_dB;
					current_power_dBm -= eq_loss_dB;
					
					if (QOT_DEBUG_OUTPUT)
						LogFile << "Power after the eq loss: " << current_power_dBm << endl << "Span loss after the eq loss: " << span_loss_dB << endl;


					// output port loss and connector at output port
					float out_power_loss_dB = src_node -> port_loss_dB[current_link -> getId()] + connector_loss_dB;
					span_loss_dB += out_power_loss_dB;
					current_power_dBm -= out_power_loss_dB;

					if (QOT_DEBUG_OUTPUT)
						LogFile << "Power after the out loss: " << current_power_dBm << endl << "Span loss after the out loss: " << span_loss_dB << endl;


					vector<OaLoc*> temp_EDFA_vect;

					for(auto itrLocOA = OaLocationList.begin(); itrLocOA != OaLocationList.end(); itrLocOA ++)
					{
						// active location at this link
						if ( (*itrLocOA) -> m_OaLocLink == current_link -> getId() && (*itrLocOA) -> m_OaLocIndicator == 1)
						{
							OaLoc* current_EDFA = *itrLocOA;
							temp_EDFA_vect.push_back(current_EDFA);
							
							if (QOT_DEBUG_OUTPUT)
								LogFile << "Location " << current_EDFA -> getOaId() << " active" << endl;

							// last preamplifier before the receiver, and we know that it is not a leaf node
							if (itrLink == (*itrPath).end() - 1 && current_EDFA -> m_OaLocLength == current_link ->	getLength() and
								current_EDFA -> next_span_known == true)
							{
								if (QOT_DEBUG_OUTPUT)
									LogFile << "PReamp that is not always a preamp" << endl;

								last_span = true;
								break;
							}

							// span length
							int current_span_length_km = current_EDFA -> m_OaLocLength - previous_location_at_link_km;
							previous_location_at_link_km = current_EDFA -> m_OaLocLength;

							if (QOT_DEBUG_OUTPUT)
								LogFile << "Span length " << current_span_length_km << endl;

							float prop_loss_dB = current_span_length_km * att_coeff_dB_km;
							span_loss_dB += prop_loss_dB;
							current_power_dBm -= prop_loss_dB;

							// connector at the end of the span (unless node and booster are directly connected)
							if(current_EDFA -> m_OaType != 1)
							{
								span_loss_dB += connector_loss_dB;
								current_power_dBm -= connector_loss_dB;
							}

							if (QOT_DEBUG_OUTPUT)
								LogFile << "Power after the prop loss: " << current_power_dBm << endl << "Span loss after the prop loss: " << span_loss_dB << endl;
							

							int first_subspan_length_km = current_span_length_km;
							
							// don't consider the fiber after the node, if any
							if(first_loc_on_link == true)
								first_subspan_length_km = temp_length_till_link_end_km;

							temp_length_till_link_end_km = current_link -> getLength() - current_EDFA -> m_OaLocLength;
							
							if (QOT_DEBUG_OUTPUT)
								LogFile << "First subspan " << first_subspan_length_km << endl;

							first_loc_on_link = false;


							current_EDFA -> gain_dB = span_loss_dB;
							current_EDFA -> limitGainComputeNF();
							
							if (QOT_DEBUG_OUTPUT)
								LogFile << "Gain to compensate for the loss " << span_loss_dB << endl << "Limited gain: " << current_EDFA -> gain_dB << endl;


							if(span_loss_dB - current_EDFA -> gain_dB > 0.1)
							{
								if (QOT_DEBUG_OUTPUT)
									LogFile << "ERROR " << span_loss_dB << " dB loss not compensated by " <<  current_EDFA -> gain_dB << " dB gain" << endl;
								
								return false;
							}


							// if span loss is less than minimum gain --> attenuate
							if(span_loss_dB < current_EDFA -> gain_dB)
							{
								current_EDFA -> att_dB = current_EDFA -> gain_dB - span_loss_dB;

								span_loss_dB += current_EDFA -> att_dB;
								current_power_dBm -= current_EDFA -> att_dB;

								if (QOT_DEBUG_OUTPUT)
									LogFile << "Power after " << current_EDFA -> att_dB << " att loss: " << current_power_dBm << endl << "Span loss after the att loss: " << span_loss_dB << endl;
							}

							else
								current_EDFA -> att_dB = 0;

							current_power_dBm += current_EDFA -> gain_dB;
							
							if (QOT_DEBUG_OUTPUT)
								LogFile << "Power after amplification: " << current_power_dBm << endl;
							

							// last preamplifier before the receiver
							if (itrLink == (*itrPath).end() - 1 && current_EDFA -> m_OaLocLength == current_link -> getLength())
							{
								last_span = true;

								if(current_EDFA -> next_span_known == false and iteration == 0)
								{
									if (QOT_DEBUG_OUTPUT)
										LogFile << "Saving preamp powers: " << current_power_dBm << endl;

									current_EDFA -> power_in_dBm = current_power_dBm;
									current_EDFA -> power_out_dBm = current_power_dBm;

									power_at_EDFA[current_EDFA -> getOaId()].push_back(current_power_dBm);
									break;
								}

							}
							

							// if there is a next span, find it to calculate the diff in power
							// to see whether the gain should be increased or decreased	

							// default launched power (max power per channel possible)
							double powerThisSpan_dBm = TRX_power_dBm;

							// default launched power (max power per channel possible)
							double powerNextSpan_dBm;

							if(iteration == 0)
							{
								// if there is fiber in the span, set the power launched into this span
								if(first_subspan_length_km != 0)
								{
									double eff_length = (1 - exp(-first_subspan_length_km * 1e3 * alpha_linear)) / alpha_linear;
									double nli_coeff = constant_nli * pow(eff_length, 2);

									double PSD_opt_cube = Planck_centFreq_Rs_baud * (current_EDFA -> gain_lin - 1) * current_EDFA -> NF_lin / (2 * nli_coeff);
									double Popt_W = cbrt(PSD_opt_cube);

									powerThisSpan_dBm = 10 * log10(Popt_W * 1e3);

									// limit it to the max possible value of 1dBm
									if (powerThisSpan_dBm > 1)
										powerThisSpan_dBm = 1;
								}

								current_EDFA -> power_in_dBm = powerThisSpan_dBm;
							
								if (QOT_DEBUG_OUTPUT)
									LogFile << "Optimum power: " << powerThisSpan_dBm << " dBm vs. actual power " << current_power_dBm << " dBm" << endl;


								if (QOT_DEBUG_OUTPUT)
									LogFile << "Looking for the next amp at the same link" << endl;

								
								vector<OaLoc*>::iterator itrLocOAnext;

								int next_first_subspan_length_km = 0;

								float next_span_loss_dB = 0;
								float next_power_dBm = current_power_dBm;

								// connector at the beginning of the next span
								if(current_EDFA -> m_OaType != 3)
								{
									next_span_loss_dB += connector_loss_dB;
									next_power_dBm -= connector_loss_dB;
								}
									
								bool nextOAfound = false;
								bool lastSpanNoPreAmp = false;

								// see if there is the next OA in the same link as the current one
								for(itrLocOAnext = OaLocationList.begin(); itrLocOAnext != OaLocationList.end(); itrLocOAnext ++)
								{
									// if there is a location further at the same link
									if ( (*itrLocOAnext) -> m_OaLocLink == current_EDFA -> m_OaLocLink && (*itrLocOAnext) -> m_OaLocLength > current_EDFA -> m_OaLocLength)
									{
										// if the location is active
										if ( (*itrLocOAnext) -> m_OaLocIndicator == 1)
										{
											if (QOT_DEBUG_OUTPUT)
												LogFile << "Amp " << (*itrLocOAnext) -> m_OaLocId << " found at the same link" << endl;

											// distance from the prev amp to the next one
											next_first_subspan_length_km = (*itrLocOAnext) -> m_OaLocLength - current_EDFA -> m_OaLocLength;
											
											// propagation loss and connector at the end of the next span
											float prop_loss_dB = next_first_subspan_length_km * att_coeff_dB_km + connector_loss_dB;
											next_span_loss_dB += prop_loss_dB;
											next_power_dBm -= prop_loss_dB;

											if (QOT_DEBUG_OUTPUT)
												LogFile << next_first_subspan_length_km << " km long subspan" << endl << "Span loss after the prop loss: " << next_span_loss_dB << endl;

											nextOAfound = true;

											break;
										}

										// if it's the last span of the demand, without a preamp
										else if (itrLink == (*itrPath).end() - 1 && current_link -> getLength() == (*itrLocOAnext) -> m_OaLocLength)
										{
											next_first_subspan_length_km = (*itrLocOAnext) -> m_OaLocLength - current_EDFA -> m_OaLocLength;
												
											// distance from the prev active location + drop loss
											float prop_loss_dB = next_first_subspan_length_km * att_coeff_dB_km;
											
											float drop_loss_dB = current_link -> dst_node -> port_loss_dB[current_link -> getId()] + filter_loss_dB;
											next_span_loss_dB += prop_loss_dB + connector_loss_dB + drop_loss_dB;
											next_power_dBm -= (prop_loss_dB + connector_loss_dB + drop_loss_dB);

											if (QOT_DEBUG_OUTPUT)
											{
												LogFile << "It's the last span of the demand" << endl;
												LogFile << next_first_subspan_length_km << " km long subspan" << endl;
												LogFile << "Span loss after the prop loss: " << next_span_loss_dB << endl;
											}

											lastSpanNoPreAmp = true;
											break;
										}
									}
								}

								// if no amps were found on the same link
								// and it's not the last link
								if(nextOAfound == false && lastSpanNoPreAmp == false)
								{
									// as we continue to the next link, first_subspan is over
									// account for the end of the prev link
									next_first_subspan_length_km = current_link -> getLength() - current_EDFA -> m_OaLocLength;
										
									float prop_loss_dB = next_first_subspan_length_km * att_coeff_dB_km;
									next_span_loss_dB += prop_loss_dB;
									next_power_dBm -= prop_loss_dB;

									if (QOT_DEBUG_OUTPUT)
									{
										LogFile << "Looking at the next links" << endl;
										LogFile << "Power after " << prop_loss_dB << " dB prop loss: " << next_power_dBm << endl;
									}

									// start from the next link 
									for(auto itrNextLink = itrLink + 1; itrNextLink != (*itrPath).end(); itrNextLink ++)
									{
										Unifiber* next_link = *itrNextLink;

										if (QOT_DEBUG_OUTPUT)
										{
											LogFile << "Next link " << next_link->getId() << endl;
											LogFile << "Src node " << next_link -> src_node -> getID() << " with input degree " << next_link -> src_node -> outDegree() << endl;
										}

										// going to the next link of the demand through a node
										float in_loss_dB = connector_loss_dB + next_link -> src_node -> port_loss_dB[next_link -> getId()];
										next_span_loss_dB += in_loss_dB;
										next_power_dBm -= in_loss_dB;

										if (QOT_DEBUG_OUTPUT)
											LogFile << "Power after " << in_loss_dB << " dB input loss is " << next_power_dBm << endl;
											
										// equalization: difference between the current power and the lowest power signal passing through the node
										float eq_loss_dB = next_power_dBm - next_link -> src_node -> lowest_power_dBm_per_output_link[next_link->getId()];
										
										if (eq_loss_dB < 0)
											eq_loss_dB = 0;
											
										next_span_loss_dB += eq_loss_dB;
										next_power_dBm -= eq_loss_dB;

										if (QOT_DEBUG_OUTPUT)
											LogFile << "Power after " << eq_loss_dB << " dB equ loss is " << next_power_dBm << endl;

										float out_loss_dB = next_link -> src_node -> port_loss_dB[next_link -> getId()] + connector_loss_dB;
										next_span_loss_dB += out_loss_dB;
										next_power_dBm -= out_loss_dB;

										if (QOT_DEBUG_OUTPUT)
											LogFile << "Power after " << out_loss_dB << " dB output loss is " << next_power_dBm << endl;
											
										for(itrLocOAnext = OaLocationList.begin(); itrLocOAnext != OaLocationList.end(); itrLocOAnext ++)
										{
											// if there is a location at this link
											if ((*itrLocOAnext) -> m_OaLocLink == next_link -> getId())
											{
												if ( (*itrLocOAnext) -> m_OaLocIndicator == 1)
												{
													if (QOT_DEBUG_OUTPUT)
														LogFile << "Amp found at loc " << (*itrLocOAnext) -> m_OaLocId << endl;
																				
													// move further along this link
													float prop_loss_dB = (*itrLocOAnext) -> m_OaLocLength * att_coeff_dB_km;
													next_span_loss_dB += prop_loss_dB;
													next_power_dBm -= prop_loss_dB;

													// connector at the end of the next span
													if((*itrLocOAnext) -> m_OaType != 1)
													{
														next_span_loss_dB += connector_loss_dB;
														next_power_dBm -= connector_loss_dB;
													}

													if (QOT_DEBUG_OUTPUT)
														LogFile << "Power after prop loss: " << next_power_dBm << endl << "Span loss after the prop loss: " << next_span_loss_dB << endl;

													nextOAfound = true;
													break;
												}

												// if it's the last span without a preamp
												else if (itrNextLink == (*itrPath).end() - 1 && next_link -> getLength() == (*itrLocOAnext) -> m_OaLocLength)
												{
													float prop_loss_dB = next_link -> getLength() * att_coeff_dB_km;
													float drop_loss_dB = next_link -> dst_node -> port_loss_dB[next_link -> getId()] + filter_loss_dB;
													
													next_span_loss_dB += prop_loss_dB + connector_loss_dB + drop_loss_dB;
													next_power_dBm -= (prop_loss_dB + connector_loss_dB + drop_loss_dB);

													if (QOT_DEBUG_OUTPUT)
													{
														LogFile << "It's the last span of the demand" << endl;
														LogFile << "Power after prop and drop loss: " << next_power_dBm << endl << "Span loss after the prop and drop loss: " << next_span_loss_dB << endl;
													}

													lastSpanNoPreAmp = true;
													break;
												}
											}
										}

										if (nextOAfound == true || lastSpanNoPreAmp == true)
											break;
											
										float prop_loss_dB = next_link -> getLength() * att_coeff_dB_km;
										next_span_loss_dB += prop_loss_dB;
										next_power_dBm -= prop_loss_dB;

										if (QOT_DEBUG_OUTPUT)
										{
											LogFile << "Going to next link" << endl;
											LogFile << "Power after prop loss: " << next_power_dBm << endl;
											LogFile << "Span loss after prop loss: " << next_span_loss_dB << endl;
										}
									}
								}


								// default launched power (max power per channel possible)
								powerNextSpan_dBm = TRX_power_dBm;

							
								// if the next amplifier was found
								// compute the power launched to that span
								if(nextOAfound == true)
								{
									// preserve the gain of the next amplifier
									double next_OA_prev_gain = (*itrLocOAnext) -> gain_dB;

									(*itrLocOAnext) -> gain_dB = next_span_loss_dB;
									(*itrLocOAnext) -> limitGainComputeNF();

									if (QOT_DEBUG_OUTPUT)
										LogFile << "Next OA " << (*itrLocOAnext) -> m_OaLocId << " found after " << next_span_loss_dB << " dB loss" << endl << "Limited gain " << (*itrLocOAnext) -> gain_dB << endl;

									// set the gain of the next OA to compensate for the loss
									if (next_span_loss_dB < (*itrLocOAnext) -> gain_dB)
									{
										float att_dB = (*itrLocOAnext) -> gain_dB - next_span_loss_dB;
										next_span_loss_dB += att_dB;

										if (QOT_DEBUG_OUTPUT)
											LogFile << "Span loss after the att loss: " << next_span_loss_dB << endl;
									}

									// if there is fiber in the span, set the power
									if(next_first_subspan_length_km != 0)
									{
										double eff_length = (1 - exp(-next_first_subspan_length_km * 1e3 * alpha_linear)) / alpha_linear;
										double nli_coeff = constant_nli * pow(eff_length, 2);

										double PSD_opt_cube = Planck_centFreq_Rs_baud * ((*itrLocOAnext) -> gain_lin - 1) * (*itrLocOAnext) -> NF_lin / (2 * nli_coeff);
										double Popt_W = cbrt(PSD_opt_cube);

										powerNextSpan_dBm = 10 * log10(Popt_W * 1e3);

										if (QOT_DEBUG_OUTPUT)
											LogFile << "Optimum power at the next span: " << powerNextSpan_dBm << endl;
									}

									// limit the launched power to the max possible value of 1dBm
									if (powerNextSpan_dBm > 1)
										powerNextSpan_dBm = 1;

									if (current_EDFA -> next_span_known == false)
									{
										current_EDFA -> next_span_known = true;
										current_EDFA -> next_span_power_dBm = powerNextSpan_dBm;
										current_EDFA -> next_OA_id = (*itrLocOAnext) -> getOaId();

										if (QOT_DEBUG_OUTPUT)
											LogFile << "Saving next power for EDFA " << current_EDFA -> getOaId() << " " << powerNextSpan_dBm << endl;
									}

									else
									{
										// more than one path from the current_EDFA to the next EDFA
										if (current_EDFA -> next_OA_id != (*itrLocOAnext) -> getOaId())
										{
											if (QOT_DEBUG_OUTPUT)
												LogFile << "More than one path from the current_EDFA to the next EDFA: " << (*itrLocOAnext) -> getOaId() << endl;
											
											current_EDFA -> next_span_power_dBm = 1;
										}
										
										powerNextSpan_dBm = current_EDFA -> next_span_power_dBm;
									}

									(*itrLocOAnext) -> gain_dB = next_OA_prev_gain;

									if((*itrLocOAnext) -> gain_dB > 0)
										(*itrLocOAnext) -> limitGainComputeNF();
								}

								// if no next amplifier was found
								else if (lastSpanNoPreAmp == true)
								{
									powerNextSpan_dBm = Prec_threshold + next_span_loss_dB;

									if(current_EDFA -> next_span_known == true and powerNextSpan_dBm < current_EDFA -> next_span_power_dBm)
									{
										if (QOT_DEBUG_OUTPUT)
											LogFile << "Reusing next power in lastSpanNoPreAmp " <<  current_EDFA -> next_span_power_dBm << " dBm" << endl;

										powerNextSpan_dBm = current_EDFA -> next_span_power_dBm;
									}

									// compensate the loss and satisfy the sensitivity of the rx
									else
									{
										if (QOT_DEBUG_OUTPUT)
											LogFile << powerNextSpan_dBm << " dBm power to achieve -18 dBm sensitivity" << endl;
									}

									// limit the launched power to the max possible value of 1dBm
									if (powerNextSpan_dBm > 1)
										powerNextSpan_dBm = 1;

									last_span = true;
								}

								else
									throw runtime_error("One of the 2 conditions must be used");
							}

							else
							{
								powerThisSpan_dBm = current_power_dBm;
								powerNextSpan_dBm = current_EDFA -> power_out_dBm;
							}
							
							double deltaPower = powerNextSpan_dBm - powerThisSpan_dBm;

							if (QOT_DEBUG_OUTPUT)
								LogFile << "deltaPower = " << powerNextSpan_dBm << " - " << powerThisSpan_dBm << " = " << deltaPower << " dBm" << endl;

							/*7 dB loss + 3 dB att = 10 dB loss = 10 dB gain
							0 dBm - (7 + 3) + 10 = 0 dBm
							
							Next span has 1 dB higher power (deltaPower = 1): 
							0 dBm - (7 + 2) + 10 = 1 dBm

							Next span has 1 dB lower power (deltaPower = -1)
							0 dBm - (7 + 4) + 10 = -1 dBm*/

							double required_gain_dB = current_EDFA -> gain_dB;

							// power at next span is higher
							if (deltaPower > 0)
							{
								if(current_EDFA -> att_dB > deltaPower)
								{
									if (QOT_DEBUG_OUTPUT)
										LogFile << "Attenuation " << current_EDFA -> att_dB << " is enough to absorb deltaPower " << deltaPower << endl;
									current_EDFA -> att_dB -= deltaPower;
								}

								else
								{
									if (QOT_DEBUG_OUTPUT)
										LogFile << "Attenuation " << current_EDFA -> att_dB << " is not enough to absorb deltaPower " << deltaPower << endl;
									
									float temp = deltaPower;
									temp -= current_EDFA -> att_dB;
									current_EDFA -> att_dB = 0;

									if (QOT_DEBUG_OUTPUT)
										LogFile << "Gain " << current_EDFA -> gain_dB << " is increased to " << current_EDFA -> gain_dB + temp << endl;

									current_EDFA -> gain_dB += temp;
									required_gain_dB = current_EDFA -> gain_dB;
								}
							}

							// power at next span is lower
							else if (deltaPower < 0)
							{
								// if gain can be decreased
								if (current_EDFA -> gain_lower_margin() > fabs(deltaPower))
								{
									if (QOT_DEBUG_OUTPUT)
										LogFile << "Gain: " << current_EDFA -> gain_dB << " can be decreased by deltaPower " << deltaPower << endl;
									
									current_EDFA -> gain_dB += deltaPower;
									
									if (QOT_DEBUG_OUTPUT)
										LogFile << "Gain is decreased to " << current_EDFA -> gain_dB << endl;

									required_gain_dB = current_EDFA -> gain_dB;
								}

								else
								{
									if (QOT_DEBUG_OUTPUT)
										LogFile << "Gain: " << current_EDFA -> gain_dB << " cannot be decreased by deltaPower " << deltaPower << endl;

									// decrease the gain till possible
									float temp = fabs(deltaPower);
									temp -= current_EDFA -> gain_lower_margin();
									current_EDFA -> gain_dB -= current_EDFA -> gain_lower_margin();
									
									// increase attenuation
									current_EDFA -> att_dB += temp;

									if (QOT_DEBUG_OUTPUT)
										LogFile << "Gain is decreased to " << current_EDFA -> gain_dB << endl << " Attenuation is increased to " << current_EDFA -> att_dB << endl;
								
									required_gain_dB = current_EDFA -> gain_dB;
								}
							}
							
							current_EDFA -> limitGainComputeNF();

							// we cannot increase gain to guarantee optimal power
							if( fabs(required_gain_dB - current_EDFA -> gain_dB) > 0.1)
							{
								if (QOT_DEBUG_OUTPUT)
									LogFile << "Cannot reach optimal power: " << required_gain_dB << " vs " << current_EDFA -> gain_dB << endl;
								return false;
							}

							current_power_dBm += deltaPower;

							power_at_EDFA[current_EDFA -> getOaId()].push_back(current_power_dBm);

							if(iteration == 0)
								current_EDFA -> power_out_dBm = current_power_dBm;

							if (QOT_DEBUG_OUTPUT)
							{
								LogFile << "Saved power " << current_power_dBm << " dBm at the output of EDFA " << current_EDFA -> getOaId() << endl;
								LogFile << "Gain " << current_EDFA->gain_dB << " Att. " << current_EDFA->att_dB << endl;
							}

							span_loss_dB = 0;

							if (last_span)
								break;

							if(current_EDFA -> m_OaType != 3)
							{
								// connector loss at the start of the next span
								span_loss_dB = connector_loss_dB;
								current_power_dBm -= connector_loss_dB;
							}
						}
					}

					temp_link_EDFAs_map[current_link -> getId()] = temp_EDFA_vect;

					if (last_span == true)
						break;

					// move to the next link
					prev_link = *itrLink;

					// no EDFAs have been found on the link
					if(first_loc_on_link)
					{
						float prop_loss_dB = current_link -> getLength() * att_coeff_dB_km;
						span_loss_dB += prop_loss_dB;
						current_power_dBm -= prop_loss_dB;

						if (QOT_DEBUG_OUTPUT)
							LogFile << "Power after the prop loss of the empty link: " << current_power_dBm << endl << "Span loss after the prop loss of the empty link: " << span_loss_dB << endl;
					}

					// end of the link after the EDFA
					else if (temp_length_till_link_end_km != 0)
					{
						float prop_loss_dB = temp_length_till_link_end_km * att_coeff_dB_km;
						span_loss_dB += prop_loss_dB;
						current_power_dBm -= prop_loss_dB;

						if (QOT_DEBUG_OUTPUT)
							LogFile << "Power after the prop loss of the link end: " << current_power_dBm << endl << "Span loss after the prop loss of the link end: " << span_loss_dB << endl;
					}
				}
			}
		}
		
		if (iteration == 0)
		{
			iteration ++;
			continue;
		}

		if(filterless)
		{
			bool one_more_iteration_required = false;

			for(auto itrNode = nodes.begin(); itrNode != nodes.end(); itrNode ++)
			{
				if ( (*itrNode) -> lowest_power_updated)
				{
					(*itrNode) -> lowest_power_updated = false;
					one_more_iteration_required = true;

					if(QOT_DEBUG_OUTPUT)
						LogFile << "Iteration " << iteration << ": Minimum power at node " << (*itrNode)->getID() << " has been updated" << endl;
				}
			}

			iteration += one_more_iteration_required;

			if(iteration > 5)
				throw runtime_error("Too many iterations");

			if(one_more_iteration_required == false)
				break;
		}

		else
			break;
	}

	if(QOT_DEBUG_OUTPUT)
	{
		for(auto itrOAgain = OaLocationList.begin(); itrOAgain != OaLocationList.end(); itrOAgain++)
			if((*itrOAgain) -> m_OaLocIndicator)
				LogFile << "Location " << (*itrOAgain) -> getOaId() << " on link " << (*itrOAgain) -> m_OaLocLink << " at " << (*itrOAgain) -> m_OaLocLength << " of type " << (*itrOAgain)->m_OaType << " with gain " << (*itrOAgain)->gain_dB << " and att " << (*itrOAgain) -> att_dB << endl;
	}

	return true;
}

// *************************************************************************************************************************
// calculatePropagatedOSNR
// recursively calculates the total OSNR ASE for the spans before the location current_loc in the filterless network
// returns the accumulated value of the OSNR ASE
pair<double, bool> Network :: calculatePropagatedSNR(OaLoc* current_loc, bool firstSpanOfDemand, set<int>& visited_links)
{
	double current_OSNR = 0;
    bool saved_value_propagated = false;

	//OA_OSNR_file << endl << endl << "Looking for propagated OSNR at loc " << current_loc -> m_OaLocId << endl;

	// if the ASE OSNR hasn't yet been accumulated before this location
	if (current_loc -> m_NoisePropagationDone == false)
	{
		//OA_OSNR_file << "Propagated OSNR unknown for location " << current_loc -> m_OaLocId << endl;

		int num_inputs = current_loc -> loc_link -> src_node -> inDegree() - 1;

        // to accumulate the 0 noise at the link itself, even if it starts with a leaf node
		if(num_inputs == 0)
			num_inputs = 1;

		//OA_OSNR_file << num_inputs << " inputs to node " << current_loc -> loc_link -> src_node -> getId() << endl; 

		// loop to account for multiple noise propagation paths in trees with multidegree nodes
		for(int i = 0; i < num_inputs; i ++)
		{
			//OA_OSNR_file << "Backtracking from location " << current_loc -> m_OaLocId << endl;
 
			// if it's not the first span and its OSNR wasn't already computed
			// second condition is needed to avoid recomputing OSNR of the prev spans on the way back to the original current_loc
			// third condition is needed when prev link has no EDFAs and we continue from the potential booster location at that link
			if (firstSpanOfDemand == false && current_loc -> current_OSNR_computed == false and current_loc -> m_OaLocIndicator == 1)
			{
				//OA_OSNR_file << "Not the first previous span - calculate the OSNR" << endl;

				// calculate the OSNR of the span
				pair<double, double> temp = spanSNR(0, 0, false, current_loc, true);

				current_OSNR = temp.first;
				current_loc -> current_OSNR_computed = true;
			}

			/*else if (firstSpanOfDemand == true)
				OA_OSNR_file << "First span - no OSNR " << endl;

			else if (current_loc -> current_OSNR_computed == true)
				OA_OSNR_file << "This span OSNR is already taken into account" << endl;*/


			// look for the prev active location and length of first subspan to find optimal power
			OaLoc* prev_loc = findPrevEDFA(current_loc, visited_links);

			// previous active location found - continue backtracking
			if (prev_loc != nullptr)
			{
				//OA_OSNR_file << "A previous location " << prev_loc -> m_OaLocId << " found in " << first_subspan_length << " km - continue the accumulation" << endl;

				pair<double, bool> temp_OSNR = calculatePropagatedSNR(prev_loc, false, visited_links);                
                current_loc -> m_AccumulatedOSNR += temp_OSNR.first;
				saved_value_propagated = temp_OSNR.second;

				//OA_OSNR_file << "Back to loc " << current_loc -> getOaId() << " at link " << current_loc -> m_OaLocLink << endl;
				//OA_OSNR_file << "Propagating saved value: " << saved_value_propagated << endl;
				//OA_OSNR_file << "Prev location " << prev_loc -> getOaId() << " was at link " << prev_loc -> m_OaLocLink << endl;


				// if the prev loc is at a different link
				if(prev_loc -> m_OaLocLink != current_loc -> m_OaLocLink)
				{
					// add temp to all the directions apart from prev_loc -> m_OaLocLink
					for(auto itrPrevLink = current_loc -> m_AccumulatedOSNRperLink.begin(); itrPrevLink != current_loc -> m_AccumulatedOSNRperLink.end(); itrPrevLink ++)
					{
						if (itrPrevLink -> first != prev_loc -> m_OaLocLink)
						{
							itrPrevLink -> second += temp_OSNR.first;
							//OA_OSNR_file << "Current loc is at link " <<  current_loc -> m_OaLocLink << endl;
							//OA_OSNR_file << temp_OSNR.first << " noise is added if the previous link is " <<  itrPrevLink -> first  << " Total is " << itrPrevLink -> second << endl;
						}
					}

					visited_links.insert(prev_loc -> m_OaLocLink);
				}

				// if OSNR was saved at the prev location and it was at the same link - break the loop
				if(prev_loc -> m_OaLocLink == current_loc -> m_OaLocLink && saved_value_propagated == true)
				{
					//OA_OSNR_file << "Escape the loop" << endl;
					break;
				}
			}

			// no preceeding OA found
			//else
			//	OA_OSNR_file << "No preceeding EDFA is found" << endl;
		}

		// calculation done 
		//OA_OSNR_file << "Calculation for location " << current_loc -> m_OaLocId << " is done" << endl;
		//OA_OSNR_file << "Accumulated noise is " << current_loc -> m_AccumulatedOSNR << endl;
		//OA_OSNR_file << "Current OSNR is " << current_OSNR << endl;
		//OA_OSNR_file << "Overall sum is " << current_loc -> m_AccumulatedOSNR + current_OSNR << endl;

		current_loc -> m_NoisePropagationDone = true; 
		current_loc -> m_AccumulatedOSNR += current_OSNR;

		return {current_loc -> m_AccumulatedOSNR, saved_value_propagated};
	}

	// accumulated ASE is already calculated and it's not an intermediate link
	else
	{
		//OA_OSNR_file << "Loc " << current_loc -> m_OaLocId << " already calculated " << endl;
		//OA_OSNR_file << "Accumulated OSNR at the location " << current_loc -> m_OaLocId << ": " << current_loc -> m_AccumulatedOSNR << endl << endl;
		return {current_loc -> m_AccumulatedOSNR, true};
	}
}

// *************************************************************************************************************************
// findPrevEDFA
// looks for the span before current_loc
// returns the previous span
// visited_links are updated if no more OAs are found at the link
OaLoc* Network :: findPrevEDFA(OaLoc* current_loc, set<int>& visited_links)
{
	OaLoc* prev_loc = nullptr;

	Unifiber* current_link = current_loc -> loc_link;

	// if this link wasn't already visited
	if(visited_links.find(current_link -> getId()) == visited_links.end())
	{
		//OA_OSNR_file << "Starting from link " << current_link -> getId() << endl; 

		int min_distance = 1e6;

		// find closest active location at the same link, before current_loc
		for (auto itrLoc = temp_link_EDFAs_map[current_link -> getId()].begin(); itrLoc != temp_link_EDFAs_map[current_link -> getId()].end(); itrLoc ++)
		{
			int temp_distance = current_loc -> m_OaLocLength - (*itrLoc) -> m_OaLocLength; 

			if (temp_distance <= 0)
				break;

			else if (temp_distance < min_distance)
			{
				min_distance = temp_distance;
				prev_loc = *itrLoc;

				//OA_OSNR_file << "Loc " << (*itrLoc) -> getOaId() << " at the same link at " << (*itrLoc) -> m_OaLocLength << " km" << endl;
			}
		}

		if (prev_loc != nullptr)
		{
			//OA_OSNR_file << endl << "Location " << prev_loc -> m_OaLocId << " is previous at the same link in " << endl;

			return prev_loc;
		}

		else
		{
			//OA_OSNR_file << "No active amplifiers found at the same link" << endl;

			// no more search on this link required
			visited_links.insert(current_link -> getId());
		}
	}

	//OA_OSNR_file << "Looking for locations at previous links " << endl;

	// go through all the incoming links
	for(auto itrLink = uni_fibers.begin(); itrLink != uni_fibers.end(); itrLink++)
	{
		// find the link that
		// leads in the opposite direction
		// wasn't already visited
		if ( (*itrLink) -> dst_node -> getID() == current_link -> src_node -> getID() and 
			(*itrLink) -> src_node -> getID() != current_link -> dst_node -> getID() and
			visited_links.find((*itrLink) -> getId()) == visited_links.end() )
		{
			//OA_OSNR_file << endl << "Previously not visited link  " << (*itrLink) -> getId() << " found " << endl;

			// if there is a filter in the node at the end of the found link - no propagation
			if (current_link -> src_node -> m_nFilter[(*itrLink) -> getId()] == true)
			{
				//OA_OSNR_file << "Filter placed after this link - no OSNR propagation" << endl << endl;
				continue;
			}

			// locations on the found link
			if (temp_link_EDFAs_map[(*itrLink) -> getId()].size() != 0)
			{
				prev_loc = temp_link_EDFAs_map[(*itrLink) -> getId()].back();
				//OA_OSNR_file << endl << "Location " << prev_loc -> m_OaLocId << " is previous" << endl;
			}
				
			// if there is no active amp at the previous link, continue searching
			else
			{
				prev_loc = temp_booster_per_link_map[(*itrLink) -> getId()];
				//OA_OSNR_file << "No active location found." << "Continuing the search from location " << prev_loc -> m_OaLocId << endl;
			}

			return prev_loc;
		}
	}
	
	//OA_OSNR_file << "No active location found" << endl;
	// couldn't find a previous amplifier - it's a first location after the leaf node
	return nullptr;
}


// ************************************************************************************************************************
// spanOSNR
// calculates 1/SNR of a given span taking into account the ASE and NLI
// returns a pair of {1/SNR_linear, Popt_dB}
// if lastSpanNoPre - only the NLI component is taken into account as there is no amplification - no ASE
// if propagated_ASE - only the ASE component is taken into account as there is no signal - no NLI
// first_subspan_length - if span includes the node, only the first subspan generates NLI
pair<double, double> Network :: spanSNR(int first_subspan_length_km, float current_power_dBm, bool lastSpanNoPre, OaLoc* current_EDFA, bool propagated_ASE)
{
	double alpha_linear = att_coeff_dB_km / (10 * log10(exp(1))) / 1e3;

	double log_func = log(pow(PI, 2) * abs(beta2) * pow(Rs_baud, 2) * pow(n_channels, 2 * Rs_baud / spacing_Hz) / alpha_linear);
    double constant_nli = (8.0 / 27.0) * alpha_linear * pow(gamma, 2) * log_func / (PI * abs(beta2) * pow(Rs_baud, 2));


	double Popt_dBm = 1;
	double NSR_lin = 1;

	// if this span doesn't include a node, it's the whole fiber length
	// otherwise, only the fiber before the node generates NLI
	double eff_length = (1 - exp(-first_subspan_length_km * 1e3 * alpha_linear)) / alpha_linear;
	double nli_coeff = constant_nli * pow(eff_length, 2);

	// last span without a pre-amp
	// gain = 0 -> no ASE
	if (lastSpanNoPre == true)
	{
		double power_last_span_W = pow(10, (current_power_dBm / 10)) / 1e3;

		// 1/SNR_NLI
		//NSR_lin = nli_coeff * pow(power_last_span_W, 3) * span_loss_lin / (power_last_span_W * span_loss_lin)
		NSR_lin = nli_coeff * pow(power_last_span_W, 2);
	}
	
	// not the last span without a preamp
	// there are both ASE and NLI
	else
	{
		if(current_EDFA -> m_OaLocIndicator == 0)
			throw runtime_error("Cannot compute SNR - no EDFA");

		if (current_EDFA -> gain_dB < 5)
			throw runtime_error("EDFA has 0 gain");

		double P_ASE = Planck_centFreq_Rs_baud * (current_EDFA -> gain_lin - 1) * current_EDFA -> NF_lin;

		// default value if there is no fiber in the span
		/*Popt_dBm = 1;

		// if there is fiber in the span, set the power
		if(first_subspan_length_km != 0)
		{
			double Popt_W = cbrt(P_ASE / (2 * nli_coeff) );
			Popt_dBm = 10 * log10(Popt_W * 1e3);

			// limit it to the max possible value of 1dBm
			if (Popt_dBm > 1)
				Popt_dBm = 1;
		}*/
		
		if(current_EDFA -> power_out_dBm < -1e3)
		{
			cout << "EDFA " << current_EDFA -> getOaId() << " has output power " << current_EDFA -> power_out_dBm << endl;
			throw runtime_error("Output power Not configured");
		}
		
		Popt_dBm = current_EDFA -> power_out_dBm;

		double power_W = pow(10, Popt_dBm / 10) / 1e3;

		// we only take into account the ASE component for the propagated OSNR
		// as there is no signal in this channel before -> no NLI
		// same for the first span of the demand followed by a booster
		if (propagated_ASE or first_subspan_length_km == 0)
			// NSR_lin = P_ASE / (power_W * span_loss_lin * gain_lin)
			NSR_lin = P_ASE / power_W; // 1/SNR_ASE

		// if there is fiber in the span, compute NLI
		else
			// NSR_lin = (P_ASE + nli_coeff * pow(power_W * span_loss_lin * gain_lin, 3) * span_loss_lin * gain_lin) / (power_W * span_loss_lin * gain_lin)
			NSR_lin = (P_ASE + nli_coeff * pow(power_W, 3) ) / power_W;
	}
	
	return {NSR_lin, Popt_dBm};
}


// ************************************************************************************************************************
// placeFilters
// places filters in the nodes if active mode is chosen
int Network :: placeFilters(int node_id)
{
	// for each node
	// find all the incoming links
	// set the filtering

	bool default_filter_state = true;
	
	if (filterless)
		default_filter_state = false;

	bool actual_filter_state = default_filter_state;

	if(node_id != -1)
		actual_filter_state = true;

	
	for (auto itrNode = nodes.begin(); itrNode != nodes.end(); itrNode++)
	{
		if(node_id != -1 && (*itrNode) -> getID() != node_id)
			continue;

		for (auto itrLink = uni_fibers.begin(); itrLink != uni_fibers.end(); itrLink++)
		{
			// find the link that ends with the node
			if ((*itrLink) -> dst_node -> getID() == (*itrNode) -> getID())
			{
				(*itrNode) -> m_nFilter[(*itrLink) -> getId()] = actual_filter_state;
				
				//cout << "Placing " << !actual_filter_state << " filter at the end of link " << (*itrLink) -> getSrc() -> getId() << " " << (*itrLink) -> getDst() -> getId() << endl;
			}
		}

		if (node_id != -1 && (*itrNode) -> getID() == node_id)
			break;
	}

	return 0;
}

// ************************************************************************************************************************
// getOppositeLinkId
// get a link ID of the link going in the opposite direction
int Network :: getOppositeLinkId(Unifiber* link)
{
	if (link == (Unifiber*) (NULL) )
		throw invalid_argument("To find a link in the opposite direction the former link should exist");

	//cout << "Looking for the opposite link of link " << link -> getId() << endl;

	// find the opposite direction link
	for(auto itrLink = uni_fibers.begin(); itrLink != uni_fibers.end(); itrLink ++)
		if (isOppositeLink(*itrLink, link))
			return (*itrLink) -> getId();

	return -1;
}

pair<float, float> Network::switching_cost()
{
	float capex_cost = 0;
	float opex_cost = 0;

	if(filterless)
	{
		vector<float> splitter_cost;

		for(int i = 0; i < 2; i ++)
			splitter_cost.push_back(0);

		splitter_cost.push_back(0.004);

		for(int i = 3; i < 5; i ++)
			splitter_cost.push_back(0.01);

		for(int i = 5; i < 9; i ++)
			splitter_cost.push_back(0.02);

		for(auto itrNode = nodes.begin(); itrNode != nodes.end(); itrNode ++)
		{
			// one splitter (combiner) per direction in each port
			for(auto port_itr = (*itrNode)->port_degree.begin(); port_itr != (*itrNode)->port_degree.end(); port_itr ++)
				capex_cost += splitter_cost[port_itr -> second];

			// one equalizer per port
			capex_cost += 1.2 * (*itrNode)->port_degree.size() / 2;
			opex_cost += 0.008 * 0.001 * 5 * 365 * 24 * (*itrNode)->port_degree.size() / 2;

			// one MUX, one DEMUX per node
			capex_cost += 2 * 0.8;

			for(auto filter_iter = (*itrNode)->m_nFilter.begin(); filter_iter != (*itrNode)->m_nFilter.end(); filter_iter ++)
				if(filter_iter -> second == true)
					capex_cost += 0.8;
		}
	}

	else
	{
		vector<float> WSS_cost;
		vector<float> WSS_power;

		for(int i = 0; i < 2; i ++)
		{
			WSS_cost.push_back(0);
			WSS_power.push_back(0);
		}

		for(int i = 2; i < 5; i ++)
		{
			WSS_cost.push_back(1.1);
			WSS_power.push_back(0.03);
		}

		for(int i = 5; i < 10; i ++)
		{
			WSS_cost.push_back(2.2);
			WSS_power.push_back(0.04);
		}

		for(int i = 10; i < 21; i ++)
		{
			WSS_cost.push_back(3);
			WSS_power.push_back(0.075);
		}

		for(auto itrNode = nodes.begin(); itrNode != nodes.end(); itrNode ++)
		{
			// one WSS per direction in each port
			for(auto port_itr = (*itrNode)->port_degree.begin(); port_itr != (*itrNode)->port_degree.end(); port_itr ++)
			{
				capex_cost += WSS_cost[port_itr -> second];
				opex_cost += WSS_power[port_itr -> second] * 0.001 * 5 * 365 * 24;
			}
			
			// one equalizer per port
			capex_cost += 1.2 * (*itrNode)->port_degree.size() / 2;
			opex_cost += 0.008 * 0.001 * 5 * 365 * 24 * (*itrNode)->port_degree.size() / 2;

			// one MUX, one DEMUX per node
			capex_cost += 2 * 0.8;
		}
	}

	capex_cost *= 1.3;
	opex_cost *= 1.75;

	return {capex_cost, opex_cost};
}

double Network :: getSizeOfUnfeasible()
{
	return listUD.size(); //return the size of the list of unfeasible demands, to check if it is empty
}

Node* Network :: lookUpNodeById(int node_id)
{
	for (auto node_itr = nodes.begin(); node_itr != nodes.end(); node_itr++)
	{
		if ((*node_itr) -> getID() == node_id)
			return (*node_itr);
	}
}

bool Network :: isOppositeLink(Unifiber* link_one, Unifiber* link_two)
{
	if (link_one -> src_node -> getID() == link_two -> dst_node -> getID() && 
			link_one -> dst_node -> getID() == link_two -> src_node -> getID())
		return true;

	else
		return false;
}

Unifiber* Network :: lookUpLinkById(int link_id)
{
	for (auto unifiber_itr = uni_fibers.begin(); unifiber_itr != uni_fibers.end(); unifiber_itr++)
	{
		if ((*unifiber_itr) -> getId() == link_id)
			return (*unifiber_itr);
	}
}


vector<bool> Network :: oa_baseline_mode(vector<Lightpath*> lps)
{

	bool fast_run = false;
	int pop_size = 1;
	double best_cost = 1e6;
	int num_unfeasible_demands = 0;
	int GA_solution_ind = 0;

	vector<vector<float>> fitness_matrix;
    fitness_matrix.push_back(vector<float>(pop_size));
    fitness_matrix.push_back(vector<float>(pop_size));

	vector<float> feasibility_vect(pop_size);

	// choose the unique solutions
	int num_unique = pop_size;

	vector<float> unique_fitness_vect(num_unique);
	vector<float> unique_secondary_fitness_vect(num_unique);
			
	// ratio from 0 to 1 for each partition
	vector<float> unique_feasibility_vect(num_unique);
	vector<bool> unfeasible;

	unique_feasibility_vect[GA_solution_ind] = 0;

	OA_OSNR_file.open("OA_OSNR_file.txt", ios::out|ios::trunc);

	// set the gains in all the network
	bool gain_can_compensate_losses = gainOAfunc(OA_OSNR_file);

	pair<double, double> OA_cost_CU(0, 0);

	double SNR_worst = 1000;
	double SNR_sum = 0;
	
	int num_paths = 0;
	int network_throughput_G = 0;

	if (gain_can_compensate_losses)
	{
		for(auto itr_loc = OaLocationList.begin(); itr_loc != OaLocationList.end(); itr_loc ++)
		{
			if ((*itr_loc) -> m_OaLocIndicator == 1)
			{
				if ( (*itr_loc) -> gain_dB < 1)
					(*itr_loc) -> m_OaLocIndicator = 0;
	
				else
				{
					OA_cost_CU.first += (*itr_loc) -> m_OaCost;
					OA_cost_CU.second += 0.008 * 0.001 * 24 * 365 * 5;
				}
			}
		}
		
		// other costs
		OA_cost_CU.first *= 1.3;
		OA_cost_CU.second *= 1.75;

		// for each demand
		for(auto itrDemand = final_lps.begin(); itrDemand != final_lps.end(); itrDemand ++)
		{
			if (filterless and (*itrDemand) -> candidate_paths.size() != 1)
				throw runtime_error("IN FON THERE CAN BE ONLY ONE PATH");

			bool all_feasible_paths = true;

			// for each of kSP path
			for(auto itrPath = (*itrDemand)->candidate_paths.begin(); itrPath != (*itrDemand)->candidate_paths.end(); itrPath ++)
			{
				pair<double, double> temp = calculateDemandSNR(OA_OSNR_file, *itrPath, (*itrDemand)->getType());
				
				double SNR_demand = temp.first;
				double P_rx = temp.second;
				
				// if (SNR_demand < SNR_threshold_dB)
				// 	continue;
				// if((*itrDemand) ->getType() == 10)
				// {
				// 	if (SNR_demand < SNR_threshold_10G)
				// 		continue;
				// }

				// else if((*itrDemand) ->getType() == 100)
				// {
				// 	if (SNR_demand < SNR_threshold_100G)
				// 		continue;
				// }	
				// else if((*itrDemand) ->getType() == 200)
				// {
				// 	if (SNR_demand < SNR_threshold_200G)
				// 		continue;
				// }

				num_paths ++;

				if (OA_placement_objective == OA_Objective::COST)
				{
					int max_bitrate_G = max_possible_throughput(SNR_demand);
					network_throughput_G += max_bitrate_G;

					vector<int> avail_bitrate_G(2, 0);

					if(max_bitrate_G >= 100)
						avail_bitrate_G[0] = 100;
						
					avail_bitrate_G[1] = max_bitrate_G;

				}

				// TODO: add weights based on path length
				SNR_sum += SNR_demand;

				if (SNR_demand < SNR_worst)
					SNR_worst = SNR_demand;

				if((*itrDemand) ->getType() == 10)
				{
					if (SNR_demand > SNR_threshold_10G && P_rx >= -18)
					{
						unfeasible.push_back(true);
					}
					else
					{
						all_feasible_paths = false;
						unfeasible.push_back(false);
					}
				}

				else if((*itrDemand) ->getType() == 100)
				{
					if (SNR_demand > SNR_threshold_100G && P_rx >= -18)
					{
						unfeasible.push_back(true);
					}
					else
					{
						all_feasible_paths = false;
						unfeasible.push_back(false);
					}
				}	
				else if((*itrDemand) ->getType() == 200)
				{
					if (SNR_demand > SNR_threshold_200G && P_rx >= -18)
					{
						unfeasible.push_back(true);
					}
					else
					{
						all_feasible_paths = false;
						unfeasible.push_back(false);
					}
				}
				else
				{
					cout<< "Oh no Oh no" <<endl;
					cin.ignore();
				}
			}

			unique_feasibility_vect[GA_solution_ind] += all_feasible_paths;
		}
	}
	else
	{
		for(auto itrDemand = final_lps.begin(); itrDemand != final_lps.end(); itrDemand ++)
		{
			unfeasible.push_back(false);
		}
	}

	// find the ratio: 0 - 1
	unique_feasibility_vect[GA_solution_ind] /= final_lps.size();


	// assign fitness values depending on the objective
	// double equip_cost = Tx_cost_CU.first + Tx_cost_CU.second + OA_cost_CU.first + OA_cost_CU.second + switch_cost_CU.first + switch_cost_CU.second;
	double equip_cost = OA_cost_CU.first + OA_cost_CU.second;

	if (OA_placement_objective == OA_Objective::COST)
	{
		unique_fitness_vect[GA_solution_ind] = equip_cost;
		unique_secondary_fitness_vect[GA_solution_ind] = -SNR_worst;
	}

	else if (OA_placement_objective == OA_Objective::MIN_SNR)
	{
		unique_fitness_vect[GA_solution_ind] = -SNR_worst;
		unique_secondary_fitness_vect[GA_solution_ind] = equip_cost;
	}
		
	else if(OA_placement_objective == OA_Objective::AV_SNR)
	{
		unique_fitness_vect[GA_solution_ind] = -SNR_sum / num_paths;
		unique_secondary_fitness_vect[GA_solution_ind] = -SNR_worst;
	}

	else if (OA_placement_objective == OA_Objective::TRAFFIC)
	{
		unique_fitness_vect[GA_solution_ind] = network_throughput_G;
		unique_secondary_fitness_vect[GA_solution_ind] = equip_cost;
	}

	else
		throw runtime_error("Unknown objective");

	// //if (unique_feasibility_vect[GA_solution_ind] >= 1.0)
	// //{
	// 	cout << "Size unfeasible "<< unfeasible.size()<<endl;
	// 	cout << "Size LPs "<< final_lps.size()<<endl;
	// 	for (int i = 0; i < unfeasible.size(); i++)
	// 	{
	// 		cout<<unfeasible[i]<<" ";
	// 	}
	// 	cout<<endl;

	// 	cout <<"This is end: "<<unique_feasibility_vect[GA_solution_ind]<<endl;
	// 	cin.ignore();
	// //}

	// just the first solution is used
	return unfeasible;

}

void Network :: get_baseline_population()
{
	// baseline placement is created in the TopoReader, written to "OA_GA_init.txt"
	// and its OSNR is computed and written to "OA_GA_OSNR.txt"
	baseline_mode = false;

	// whether we account for ASE propagation
	filterless = false;
	blockers = false;

	OA_placement_objective = OA_Objective::COST;

    map<int, float> port_loss_map;

	for(int degree = 1; degree < 8; degree ++)
		port_loss_map[degree] = 3 * ceil(log(degree) / log(2));


	// set port_degree in every node of the network (or a tree)
	for(auto node_itr = nodes.begin(); node_itr != nodes.end(); node_itr ++)
	{
		(*node_itr) -> port_loss_dB.clear();
		
		// cannot just use AbstractNode :: m_hILinkList, 
		// as the same node can be included in different filterless trees
		vector<int> adj_links;

		for(auto link_itr = uni_fibers.begin(); link_itr != uni_fibers.end(); link_itr ++)
			if ((*node_itr) -> getID() == (*link_itr) -> dst_node -> getID() or (*node_itr) -> getID() == (*link_itr) -> src_node -> getID() )
				adj_links.push_back((*link_itr)->getId());

		if (adj_links.size() % 2 != 0)
			throw runtime_error("Weird node degree");

		float loss_dB = 0;

		// WSS has a fixed loss, independent on the number of ports
        if(filterless == false)
            loss_dB = filter_loss_dB;

		// splitter/combiner loss depends on the number of ports
        else
            loss_dB = port_loss_map[adj_links.size() / 2];

		// TO CHECK
		if (loss_dB == 0)
			loss_dB = 3;

		for(auto link_itr = adj_links.begin(); link_itr != adj_links.end(); link_itr ++)
		{
			(*node_itr) -> port_loss_dB[*link_itr] = loss_dB;
			(*node_itr) -> port_degree[*link_itr] = adj_links.size() / 2;
        }
	}

	if (filterless and blockers)
	{
		filterless = false;
		placeFilters();
		filterless = false;
	}

	bool fast_run = false;
	int pop_size = 1;
	double best_cost = 1e6;
	int num_unfeasible_demands = 0;

	// first define the structure of the chromosome - order of genes (or gene clusters) and their weights
	vector<vector<float>> chromosome_struct;

	vector<float> temp_booster;
	temp_booster.push_back(OaLoc :: booster_cost);

	vector<float> temp_preamp;
	temp_preamp.push_back(OaLoc :: preamp_cost);

	vector<float> temp_ILA;
	temp_ILA.push_back(OaLoc :: ILA_booster_cost);

	// then assign the weights to the locations
	for (auto itrLoc = OaLocationList.begin(); itrLoc != OaLocationList.end(); itrLoc ++)
	{
		// booster
		if ((*itrLoc) -> m_OaType == 1)
			chromosome_struct.push_back(temp_booster);

		// ILA
		else if ((*itrLoc) -> m_OaType == 2)
			chromosome_struct.push_back(temp_ILA);

		// preamp
		else if ((*itrLoc) -> m_OaType == 3)
			chromosome_struct.push_back(temp_preamp);

		else
			throw runtime_error("getOaLoc_GA. Unknown EDFA type");
	}
		
	// construct a GA object
	// GeneticAlgorithm GenAmpPlacement(pop_size, chromosome_struct, GeneticAlgorithm :: OA_placement_single);
	GeneticAlgorithm_OA GenAmpPlacement(pop_size, chromosome_struct, GeneticAlgorithm_OA :: OA_placement_single, false, fast_run);

	// generate random solutions and place baseline as the first one
	GenAmpPlacement.first_generation();

	GenAmpPlacement.create_solution(create_SNRaware_minOTN_OAplacement(), false, 0);

	// to accound only the unique solutions
	vector<int> matching_list_solutions;

	// choose the unique solutions
	int num_unique = GenAmpPlacement.find_unique_solutions(matching_list_solutions);

	// go through all the locations and place amplifiers and filters
	for(int gene_ind = 0; gene_ind < OaLocationList.size(); gene_ind ++)
	{
		OaLocationList[gene_ind] -> m_OaLocIndicator = (int)(GenAmpPlacement.is_selected_gene_unique_active(0, gene_ind));
	}
}


vector<bool> Network::create_SNRaware_minOTN_OAplacement()
{
	gene_length = OaLocationList.size();

	// read the file with the initial placements
	ifstream InitFile(INIT_FILE_NAME_OA_V3, ios::in);

	if (!InitFile.is_open())
		throw ifstream::failure("Failed to open the init file" + string(INIT_FILE_NAME_OA_V3));

	int amp_counter;
	int start, end;
	string buf, data;
	string s_init_placement = "Initial placement";

	int init_placement_num, cand_location_id;

	vector<bool> temp;


	while(!InitFile.eof())
	{
		// first line
		getline(InitFile, buf);

		// if it's commented, skip
		if (buf.find("//") != -1)
			continue;

		// skip the title
		start = buf.find(s_init_placement);
		if (start == string::npos)
			continue;

		// read the number and get rid of the spaces
		data = buf.substr(start + s_init_placement.length());
		data.erase( remove_if( data.begin(), data.end(), ::isspace ), data.end() );

		// the number of the members in the population
		init_placement_num = stoi(data);

		// no overflow
		if (init_placement_num >= 1)
			throw invalid_argument("Initial placement is out of range");
		
		amp_counter = 0;

		// second line
		getline(InitFile, buf);

		// extract the id list from the brackets
		start = buf.find("<");
		end = buf.find(">");

		if (start == string::npos || end == string::npos)
			continue;

		buf = buf.substr(start + 1, end - start - 1);

		// delete the spaces
		buf.erase( remove_if( buf.begin(), buf.end(), ::isspace ), buf.end() );

		end = 0;

		temp.clear();
		temp.resize(gene_length, 0);

		// go till the last delimiter is found
		while(true)
		{
			// find the next delimiter
			end = buf.find(";");

			if (end == string::npos)
				break;

			// extract the data till the delimiter
			data = buf.substr(0, end);

			// the postiion of the placed amplifier
			cand_location_id = stoi(data);

			// no overflow
			if (cand_location_id >= gene_length)
				throw invalid_argument("Candidate location id is out of range");

			// cut the processed part of the string
			buf = buf.substr(end + 1);

			temp[cand_location_id] = true;
				
		}
	}

	InitFile.close();

	return temp;

}

// void Network :: GA_initializer1(int population_size)
// {
	
// 	for (int i = 0; i < population_size; i++)
// 	{
// 		vector <int> temp_vector;
// 		for (int j = 0 ; j < connection_requests.size(); j++)
// 		{
// 			int cluster_size = 0;
// 			if (connection_requests[j]->getCapacity() > float(10))
// 			{
// 				cluster_size = ext_candidate_paths_100[connection_requests[j]->getNodePairIndex()].size();
// 			}

// 			else
// 			{
// 				cluster_size = ext_candidate_paths_10[connection_requests[j]->getNodePairIndex()].size();
// 			}

// 			int random_number = rand() % cluster_size; 
// 			temp_vector.push_back(random_number);
// 		}
// 		GA_initializer_vector.push_back(temp_vector);
// 	}

// }