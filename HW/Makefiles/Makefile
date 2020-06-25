
TARGET = kmp
CXX = g++
CXXFLAGS = -o3

.PHONY: bin/sw_check

bin/sw_check: sw/kmp.o test_functions/kmp_test.o
	$(CXX) $^ -o $@ 

sw/kmp.o: sw/kmp.cpp
	$(CXX) -c $(CXXFLAGS) -Itest_functions $< -o $@

test_function/kmp_test.o: test_functions/kmp_test.cpp
	$(CXX) -c $(CXXFLAGS) -Itest_functions $< -o $@

clean:
	rm -f test_function/*.o sw/*.o bin/$(TARGET)