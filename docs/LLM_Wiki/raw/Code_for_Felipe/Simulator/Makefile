CPP = g++
CPPOPT = -ggdb -std=c++17 -O1 -Wall -Wno-sign-compare#prima era -g0
CFLAGS = -g -Wall -Wextra
# CPPOPT = -g -D_OCHDEBUGA
LINKOPT =
CMD = $(CPP) $(CPPOPT)
# generate objective files under ./linuxd for debug; ./linuxr for release
ObjDir = linuxr
Executable = NBGA

ObjFiles = $(ObjDir)/NBGA_Main.o $(ObjDir)/GA_Solution.o  $(ObjDir)/GeneCluster.o $(ObjDir)/GeneticAlgorithm.o $(ObjDir)/Connection.o $(ObjDir)/Graph.o $(ObjDir)/Network.o $(ObjDir)/Node.o $(ObjDir)/Unifiber.o $(ObjDir)/Lightpath.o $(ObjDir)/DijkstraShortestPathAlg.o $(ObjDir)/YenTopKShortestPathsAlg.o $(ObjDir)/GA_Solution_OA.o  $(ObjDir)/GeneCluster_OA.o $(ObjDir)/GeneticAlgorithm_OA.o $(ObjDir)/OaLoc.o $(ObjDir)/OchObject.o

$(Executable): $(ObjFiles)
	$(CMD) -o $@ $(ObjFiles)

$(ObjDir)/NBGA_Main.o: NBGA_Main.cpp
	$(CMD) -c NBGA_Main.cpp -o $@

$(ObjDir)/GA_Solution.o: GA_Solution.cpp
	$(CMD) -c GA_Solution.cpp -o $@

$(ObjDir)/GeneCluster.o: GeneCluster.cpp
	$(CMD) -c GeneCluster.cpp -o $@

$(ObjDir)/GeneticAlgorithm.o: GeneticAlgorithm.cpp
	$(CMD) -c GeneticAlgorithm.cpp -o $@

$(ObjDir)/Connection.o: Connection.cpp
	$(CMD) -c Connection.cpp -o $@

$(ObjDir)/Graph.o: Graph.cpp
	$(CMD) -c Graph.cpp -o $@

$(ObjDir)/Network.o: Network.cpp
	$(CMD) -c Network.cpp -o $@

$(ObjDir)/Node.o: Node.cpp
	$(CMD) -c Node.cpp -o $@

$(ObjDir)/Unifiber.o: Unifiber.cpp
	$(CMD) -c Unifiber.cpp -o $@

$(ObjDir)/Lightpath.o: Lightpath.cpp
	$(CMD) -c Lightpath.cpp -o $@

$(ObjDir)/DijkstraShortestPathAlg.o: DijkstraShortestPathAlg.cpp
	$(CMD) -c DijkstraShortestPathAlg.cpp -o $@

$(ObjDir)/YenTopKShortestPathsAlg.o: YenTopKShortestPathsAlg.cpp
	$(CMD) -c YenTopKShortestPathsAlg.cpp -o $@
	

$(ObjDir)/OaLoc.o: OaLoc.cpp
	$(CMD) -c OaLoc.cpp -o $@

$(ObjDir)/OchObject.o: OchObject.cpp
	$(CMD) -c OchObject.cpp -o $@

$(ObjDir)/GA_Solution_OA.o: GA_Solution_OA.cpp
	$(CMD) -c GA_Solution_OA.cpp -o $@

$(ObjDir)/GeneticAlgorithm_OA.o: GeneticAlgorithm_OA.cpp
	$(CMD) -c GeneticAlgorithm_OA.cpp -o $@

$(ObjDir)/GeneCluster_OA.o: GeneCluster_OA.cpp
	$(CMD) -c GeneCluster_OA.cpp -o $@
clean:
	rm -f $(ObjDir)/*.o