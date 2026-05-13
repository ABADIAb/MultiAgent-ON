#ifndef UNIFIBER_H
#define UNIFIBER_H

#include <list>
#include <iostream>
#include <vector>

using namespace std;

namespace NS_NBGA
{
    class Node;
    class Unifiber 
    {
        public:

            Unifiber(int nFiberId, int nSrcID, int nDstID, float nFiberCapacity, float nFiberLength);
            

            // functions which return the parameters of the fiber

            int getId() const { return m_FiberId; };

            int getSrcId() const { return m_SrcId; };

            int getDstId() const { return m_DstId; };

            float getCapacity() const { return m_FiberCapacity; };

            float getLength() const { return m_FiberLength; };

            Node*       src_node;

            Node*       dst_node;

        protected:

            // variables use for saving the parameters of the fiber 

            int			m_FiberId;
            float   	m_FiberCapacity;
            float	    m_FiberLength;
            int	        m_SrcId;
            int	        m_DstId;
    };
};

#endif