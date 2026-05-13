#include "Node.h"

using namespace NS_NBGA;
using namespace std;

Node :: Node(int Node_ID, int Node_Check)
{
    node_id = Node_ID;
    node_check = Node_Check;
}

int Node :: inDegree() const
{
	return in_fibers.size();
}

int Node :: outDegree() const
{
	return out_fibers.size();
}