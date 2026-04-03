
#include "xspcomm/xcomm.h"

void uart(uint64_t c, void *p){
    xspcomm::XData** pins = (xspcomm::XData **)p;
    if ((*pins[0]) != 0){
        fprintf(stderr,"%c", (char)(*pins[1]));
    }
}
