#include "OaLoc.h"
//#include "OchObject.h"

#include <stdexcept>
#include <cmath>
using namespace NS_NBGA;


OaLoc :: OaLoc() {}

OaLoc :: OaLoc(int OaLocId, int OaLocLink, int OaLocLength, int OaLocInd, double OaGain, double OaNF, int OaType):
        m_OaLocId(OaLocId), m_OaLocLink(OaLocLink), m_OaLocLength(OaLocLength), m_OaLocIndicator(OaLocInd), gain_dB(OaGain), NF_dB(OaNF), m_OaType(OaType)
{
    if (m_OaType == 1)
        m_OaCost = booster_cost;

    else if (m_OaType == 2)
        m_OaCost = ILA_booster_cost;

    else if (m_OaType == 3)
        m_OaCost = preamp_cost;
    
    else
        throw std::invalid_argument("Unknown amp type");
}


int OaLoc :: reset(Unifiber* link)
{
    gain_dB = 0;
	att_dB = 0;
	NF_dB = 0;

    gain_lin = 1;
    NF_lin = 1;
    
	loc_link = link;

    next_span_known = false;
    next_span_power_dBm = -1e6;
    next_OA_id = -1;

	m_SNR_saved = false;
	m_span_SNR = 0;
	power_in_dBm = -1e6;
    power_out_dBm = -1e6;

	m_AccumulatedOSNR = 0;
	m_NoisePropagationDone = false;
	current_OSNR_computed = false;

    // m_AccumulatedOSNRperLink.clear();
}


// set a subtype according to the cost
/*int OaLoc :: setType(double cost)
{
    if (this -> m_OaType == 1)
    {
        if (cost == booster_cost)
            this -> m_OaCost = booster_cost;

        else
            throw std::invalid_argument("Wrong cost for the booster");
        
    }

    else if (this -> m_OaType == 2)
    {
        if (cost == ILA_booster_cost)
            this -> m_OaCost = ILA_booster_cost;
        else
            throw std::invalid_argument("Wrong cost for the ILA");
        
    }

    else if (this -> m_OaType == 3)
    {
        if (cost == preamp_cost)
            this -> m_OaCost = preamp_cost;
        
        else
            throw std::invalid_argument("Wrong cost for the ILA");
    }

    else
        throw std::invalid_argument("Unknown amp type");
    
    return 0;
}*/


// ************************************************************************************************************************
// limitgain
// if the gain of the amplifier exceeds a min or max threshold, limit it accordingly
// compute NF based on the gain
int OaLoc :: limitGainComputeNF()
{
	double a, b;

	// booster
	if (m_OaType == 1 or m_OaType == 2)
	{
		if (gain_dB < booster_min_gain)
			gain_dB = booster_min_gain;
		
		else if (gain_dB > booster_max_gain)
			gain_dB = booster_max_gain;

		a = coeff_a_booster;
		b = coeff_b_booster;
	}

	// pre-amp
	else if (m_OaType == 3)
	{
		if (gain_dB < preamp_min_gain)
			gain_dB = preamp_min_gain;
			
		else if (gain_dB > preamp_max_gain)
			gain_dB = preamp_max_gain;

		a = coeff_a_preamp;
		b = coeff_b_preamp;
	}
	
	else
		throw std::invalid_argument("limitGainComputeNF. Unknown EDFA type");

	// set the noise figure of the OA according to its gain
	gain_lin = pow(10, (gain_dB / 10));
		
	NF_lin = a + (double)(b / (gain_lin - 1));
	NF_dB = 10 * log10(NF_lin);

	return 0;
}


float OaLoc :: gain_lower_margin()
{
    double min_gain_dB = 0;

    // booster
	if (m_OaType == 1 or m_OaType == 2)
        min_gain_dB = booster_min_gain;

	// pre-amp
	else if (m_OaType == 3)
        min_gain_dB = preamp_min_gain;

    double lower_margin_dB = gain_dB - min_gain_dB;

    if (lower_margin_dB < 0)
        throw std::invalid_argument("Lower margin cannot be negative");

    return lower_margin_dB;
}