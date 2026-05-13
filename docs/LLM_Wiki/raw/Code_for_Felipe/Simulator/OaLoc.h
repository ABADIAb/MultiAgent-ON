#ifndef OALOC_H
#define OALOC_H

#include "OchObject.h"
#include <map>

namespace NS_NBGA
{
    class Unifiber;
    class OaLoc: public OchObject 
    {
        public:
            OaLoc();
            OaLoc(int, int, int, int, double, double, int); 
            
        // *******************************************************************************
        // Variables

            int m_OaLocId;
            int m_OaLocLink;
            int m_OaLocLength;      // need to be changed to m_OaLocPosition
            int m_OaLocIndicator;   // need to be changed to m_OaLocBool

            Unifiber* loc_link;

            double gain_dB;        // set the gain of the OA
            double att_dB;
            double NF_dB;          // noise figure


            double gain_lin;
            double NF_lin;

            bool next_span_known;
            double next_span_power_dBm;
            int next_OA_id;
            
            int m_OaType;           // 1-booster, 2-ILA, 3-preamp

            //added by OLEG
            bool m_NoisePropagationDone;
            double m_AccumulatedOSNR;
            std::map<int, double> m_AccumulatedOSNRperLink;

            bool current_OSNR_computed;

            bool m_SNR_saved;
            double m_span_SNR;
            double power_in_dBm;
            double power_out_dBm;

            double m_OaCost;

            static constexpr double booster_cost = 4.85;
            static constexpr double preamp_cost = 4.85; //0.5;
            static constexpr double ILA_booster_cost = 8.1;

            static constexpr double gain_safety_margin_dB = 1;

            static constexpr double booster_min_gain = 10;
            static constexpr double booster_max_gain = 24 - gain_safety_margin_dB;

            static constexpr double preamp_min_gain = 10;//18;
            static constexpr double preamp_max_gain = 24 - gain_safety_margin_dB;//34 - gain_safety_margin_dB;

            static constexpr double coeff_a_booster = 2.793;
            static constexpr double coeff_b_booster = 117.513;
            static constexpr double coeff_a_preamp = 2.793;//3.88;
            static constexpr double coeff_b_preamp = 117.513;//457.586;

        // *******************************************************************************
        // Functions

            int getOaId() { return m_OaLocId; }
            int reset(Unifiber* link);
            int getObjectType() { return OchObject :: amp_type_id; }

            float gain_lower_margin();
            int limitGainComputeNF();

            // set a subtype according to the cost
            int setType(double cost);
    };
};

#endif