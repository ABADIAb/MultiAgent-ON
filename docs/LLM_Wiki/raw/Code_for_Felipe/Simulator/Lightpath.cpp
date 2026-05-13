#include "Lightpath.h"


using namespace NS_NBGA;

Lightpath::Lightpath(int Interface1, int Interface2, int lp_type, vector<Unifiber*> Fiberset)
{
    m_interface1 = Interface1;
    m_interface2 = Interface2;
    m_type = lp_type;
    fibers = Fiberset;
    candidate_paths.push_back(Fiberset);

}