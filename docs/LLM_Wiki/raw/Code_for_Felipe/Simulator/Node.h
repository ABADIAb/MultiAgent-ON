#ifndef NODE_H
#define NODE_H

#include <vector>
#include <map>

using namespace std;


namespace NS_NBGA 
{
	class Unifiber;
	class Node 
	{
		public:
            
			Node(int Node_Id,int Nodecheck );

			int getID() const { return node_id; };
			int getNodeCheck() const {return node_check; };
			int inDegree() const;
			int outDegree() const;
			map<int, bool> m_nFilter;

			vector<Unifiber*> in_fibers;

			vector<Unifiber*> out_fibers;

			map<int, float> port_loss_dB;
			map<int, int> port_degree;

			// lowest power per outgoing link
			map<int, float> lowest_power_dBm_per_output_link;
			bool lowest_power_updated;

		protected:

			int node_id;
			int node_check;

	};
};

#endif