#ifndef CONNECTION_H
#define CONNECTION_H

#include <iostream>
#include <vector>
#include <tuple>

using namespace std;

namespace NS_NBGA
{
    class Connection 
    {
        public:

            Connection(int nConnectionId, int nSrcID, int nDstID, float nConnectionCapacity, int nConnectionProtection, int nRoutingType);
            

            // functions which return the parameters of the fiber

            int getId() const { return m_ConnectionID; };

            int getSrcID() const { return m_SrcID; };

            int getDstID() const { return m_DstID; };

            float getCapacity() const { return m_ConnectionCapacity; };

            int getProtection() const { return m_Protection; };
            
            int RoutingType ()  const { return m_RoutingType; };

            int getNodePairIndex() const { return m_NodePairIndex; };

            vector<int> getMainPath() { return m_MainPath; };

            vector<tuple<int, int> > getMainLPs() { return m_MainLPs; };


            // functions which will be used for setting some parameters

            void setNodePairIndex(int nNodePairIndex) { m_NodePairIndex = nNodePairIndex; };
            
            void setMainPath(vector<int> MainPath) { m_MainPath.clear(); m_MainPath = MainPath; };

            void setMainLPs(vector<tuple<int, int> > MainLPs) { m_MainLPs.clear(); m_MainLPs = MainLPs; };

            

        public:
            vector<int> groups_unprotected;
            vector<int> groups_protected1;
            vector<int> groups_protected2; 

        protected:
            int			m_ConnectionID;
            int	        m_SrcID;
            int	        m_DstID;
            float   	m_ConnectionCapacity;
            int         m_Protection;   
            int			m_NodePairIndex;  
            int         m_RoutingType;
            vector<int>    m_MainPath;
            vector<tuple<int, int> > m_MainLPs;           
    };
};

#endif