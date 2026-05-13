#ifndef LIGHTPATH_H
#define LIGHTPATH_H

#include <list>
#include <iostream>
#include <vector>
#include "Unifiber.h"
using namespace std;

namespace NS_NBGA 
{
    class Lightpath 
    {
        public:

            Lightpath(int Interface1, int Interface2, int lp_type, vector<Unifiber*> Fiberset);

            int get_id() const { return id; };

            void set_id(int lp_id) { id = lp_id; };
            
            int getEndId1() const { return m_interface1; };

            int getEndId2() const { return m_interface2; };

            int getType() const { return m_type; };
            

            void insert_connection(int ConnectionID) { routed_connections.push_back(ConnectionID); };
            void add_used_capacity(double used_capacity) 
            { 
                capacity_used += used_capacity;
                if (capacity_used > 100 && m_type == 100)
                    m_type = 200; 
            };

            float get_lp_length()
            {
                float sum = 0;
                for (auto itr = candidate_paths[0].begin(); itr != candidate_paths[0].end(); itr++)
                {
                    sum += (*itr)->getLength();
                }

                return sum;
            };
            
            vector<int> routed_connections;
            vector<Unifiber*> fibers;
            vector<vector<Unifiber*> > candidate_paths;
            double      capacity_used;

        protected:
            int         id;
            int	        m_interface1;
            int	        m_interface2;
            int         m_type;
    };
};

#endif