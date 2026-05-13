#ifndef OCHOBJECT_H
#define OCHOBJECT_H

#include <iostream>

using namespace std;
namespace NS_NBGA {

class OchObject {
public:
	OchObject();
	virtual ~OchObject();

	// for debugging
	virtual const char* toString() const;
	virtual void dump(std::ostream& out) const;


	// added by Oleg
	static const int node_type_id = 3;
	static const int amp_type_id = 4;

	// type of the object
	virtual int getObjectType() { return 0; }
};
};	// namespace
#endif