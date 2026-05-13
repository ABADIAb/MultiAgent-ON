#include "Connection.h"


using namespace NS_NBGA;

Connection::Connection(int nConnectionId, int nSrcID, int nDstID, float nConnectionCapacity, int nConnectionProtection, int nRoutingType)
{
    m_ConnectionID = nConnectionId; // set connection id
	m_ConnectionCapacity = nConnectionCapacity; // set connection capacity
    // set protection code
    // 0 means, connection is not protected
    // 1 means, connection is protected and this is the first instance of the two connections
    // 2 means, connection is protected and this is the second instance of the two connections 
    m_Protection = nConnectionProtection;
    m_SrcID = nSrcID; // set source id of the connection
    m_DstID = nDstID; // set destination id of the connection
    m_RoutingType = nRoutingType;
}