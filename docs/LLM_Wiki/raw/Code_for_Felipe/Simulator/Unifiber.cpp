#include "Unifiber.h"


using namespace NS_NBGA;

Unifiber::Unifiber(int nFiberId, int nSrcID, int nDstID, float nFiberCapacity, float nFiberLength)
{
    m_FiberId = nFiberId; // set fiber id
	m_FiberCapacity = nFiberCapacity; // set fiber capacity
    m_FiberLength = nFiberLength; // set fiber length
    m_SrcId = nSrcID; // set source id of the fiber
    m_DstId = nDstID; // set destination id of the fiber
}