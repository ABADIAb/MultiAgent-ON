#ifndef NETWORK_H
#define NETWORK_H

#define INIT_FILE_NAME_OA_V3 "OA_GA_init_v3.txt"


#include <vector>
#include <list>
#include <iostream>
#include <fstream> 
#include <tuple>
#include <limits>
#include <set>
#include <map>
#include <queue>
#include <string>
#include <vector>
#include <fstream>
#include <iostream>
#include <algorithm>
//#include "Graph.h"
#include "Unifiber.h"
#include "Connection.h"
#include "Lightpath.h"
#include "GeneticAlgorithm.h"
#include "Node.h"
#include "GraphElements.h"
#include "Graph.h"
#include "YenTopKShortestPathsAlg.h"
#include "OaLoc.h"
#include "GA_Solution_OA.h"
#include "GeneticAlgorithm_OA.h"

namespace NS_NBGA 
{
	class Network 
	{
		public:

			Network();
			
			double getOaLoc_GA(ofstream& LogFile, bool fast_run = false);
			
			bool initialize(const char* pInputFile, int MultiThread, int NumberLambdas, int max_number_gen, float years_input, const char* result_file_name);

			int getNumberOfConnectionRequests() const { return number_connection_requests; };
			int getNumberOfNodes() const { return number_nodes; };
			int getNumberOfUniFibers() const { return number_uni_fibers; };
			void get_baseline_population();
			vector<GA_Solution_OA> population;
			int gene_length;
			vector<bool> oa_baseline_mode(vector<Lightpath*> lps);

			vector<vector<int> > mutation_importance();
			
			void runExternalGA();

			void set_selected_paths (vector<int> selected_candidates);
			tuple<float, float> calculate_feasibility_fitness(bool print_results = false);

			vector<OaLoc*> OaLocationList;
			

	        OaLoc* addOaLoc(int OaLocId, int OaLocLink, int OaLocLength, int OaLocInd, double OaGain, double OaNF, int OaType);
			pair<double, double> calculateDemandSNR(ofstream& LogFile, vector<Unifiber*>& path, int lp_type);
            pair<double, bool> calculatePropagatedSNR(OaLoc* current_loc, bool firstSpanOfDemand, set<int>& visited_links);
            pair<double, double> spanSNR(int first_subspan_length_km, float current_power_dBm, bool lastSpanNoPre, OaLoc* loc, bool propagated_ASE = false);
			OaLoc* findPrevEDFA(OaLoc* current_loc, set<int>& visited_links);
			vector<vector<int> > GA_initializer(int population_size);
			
			void addTopoNode(int, int);
			void addUniFiber(int, int, int, float, int);
			void addConnectionRequest(int, int, int, float , int, int);

			bool readTopo(const char*);
			bool readTopoHelper(ifstream&);
			void getPaths();
			int calculateTotalVertices(int node_vertices, vector <Node* > node_list);

			void CheckOBSolution();
			bool gainOAfunc(ofstream& file);
            double OAPlacement(bool fast_run = false);
			int OAPlacement_base();
			int placeFilters(int node_id = -1);
            bool ampSetToMaxGain(OaLoc* loc);
            int limitGainComputeNF(OaLoc* loc);
			int getOppositeLinkId(int);
			int getOppositeLinkId(Unifiber* link);
            // functions for the OSNR calculation
	        double QoTcalc2(Lightpath *lp);
			double getSizeOfUnfeasible();
			vector<bool> create_SNRaware_minOTN_OAplacement();
			int Baseline_model(vector <Lightpath*> LP_check);
		
			void mapRequestToPair();

			Node* lookUpNodeById(int node_id);
			Unifiber* lookUpLinkById(int link_id);
			bool isOppositeLink(Unifiber* link_one, Unifiber* link_two);
			pair<float, float> switching_cost();



			ofstream OA_OSNR_file;
            ofstream OA_GA_GAIN;
	        ofstream OA_file;
			ofstream FileHops, FileDemands;

			list<Unifiber*> listUL;

			list<Lightpath*> listUD;

			enum class OA_Objective {COST, MIN_SNR, AV_SNR, TRAFFIC};
			OA_Objective OA_placement_objective;




		protected:
			int number_nodes;
			int number_uni_fibers;
			int number_connection_requests;
			bool multi_thread;
			bool blockers;
			int number_lambdas;
			int max_number_generation;
			int objective;
			int node_loss_km;             // attenuation in km equivalent to the node loss (different for active and filterless)

			int baseline_run = 0;
			bool flexible_preamps;           //whether preamps can be chosen to be boosters or preamps
	        bool flexible_ILAs;              //whether ILAs can be chosen to be boosters or preamps
            bool baseline_mode = false;
            bool power_shaping;          	//whether we use power shapers in the nodes
	                                        //they stop ASE propagation and allow wavelength reuse 
            bool averaging_mode = false;            // simulator is shut down after each run of GA
            bool predefined_threshold_mode = false; // OSNR threshold is read from the OA_GA_threshold.txt file
            bool demands_creation_mode;
            bool filterless;
            bool attenuation;

			float length_lp = 0;
		
			
			

			const char* result_file_n;

			float years;

			double SNR_threshold_10G = 12.2;
			double SNR_threshold_100G = 8.6;
			double SNR_threshold_200G = 15.2;

			

			//double OSNR_threshold_10G_BL = 19;
			//double OSNR_threshold_100G_BL = 15;
			//double OSNR_threshold_200G_BL = 24;
            double loss_coeff;
            double min_path_km, max_path_km;
	        double avg_path_km, sum_paths_km, sum_paths_loss;
			
			

			vector<Node*>  	   		nodes;
			vector<Unifiber*>  		uni_fibers;
			vector<Connection*> 	connection_requests;
			vector<Connection*> 	node_pair_requests;
			vector<Lightpath*>      final_lps;

			
			vector<vector<vector<int> > > ext_candidate_paths_10;
			vector<vector<vector<int> > > ext_candidate_paths_100;

			vector<vector<vector<tuple<int, int> > > > ext_candidate_LPs_10;
			vector<vector<vector<tuple<int, int> > > > ext_candidate_LPs_100;


			vector<int> OAsPlaced;
	        vector<int> preOAplaced;
	        vector<int> boosterOAplaced;
	        vector<int> ILAplaced;
            vector< vector<int> > vecOfVec;


			map<int, vector<OaLoc*>> temp_link_EDFAs_map;
			map<int, OaLoc*> temp_preamp_per_link_map;
			map<int, OaLoc*> temp_booster_per_link_map;

			map<int, vector<float>> power_at_EDFA;
			map<int, vector<float>> power_at_EDFA_second;

			map<int, float> in_out_port_loss_dB_map;


			double Prec_threshold = -18;
	
			double SNR_threshold_dB = 6.7 + 2;

			double gamma = 1.27 / 1e3;
			double PI = 3.1415926;
			double c_band = 5e12;
			double beta2 = 21.7e-27;
			double Planck = 6.62607004e-34;
			double centFreq = 193.4e12;
			double Rs_baud = 32e9;
			double att_coeff_dB_km = 0.25;
			double spacing_Hz = 50e9;

			float filter_loss_dB = 6;
			float connector_loss_dB = 1;


			double Planck_centFreq_Rs_baud = Planck * centFreq * Rs_baud;
			double n_channels = c_band / spacing_Hz;


        	vector<int> FSU_per_demand; // number of FSU for each demand routed

			//number of the candidate locations for placing OA in the network - Added by MEM(25Jan)
			int numcandloc;
		
	};
};

#endif