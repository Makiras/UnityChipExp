#include <svdpi.h>
#include <stdio.h>

#ifdef __cplusplus
extern "C" {
#endif
void xs_assert_v2(const char* filename, long long line){
	printf("%ld:%s\n", line, filename);
}

#ifdef __cplusplus
}
#endif
