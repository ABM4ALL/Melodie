#include <stdio.h>
#include <stdlib.h>
typedef int int32;
typedef unsigned int uint32;
typedef struct
{
    uint32 length;
    int32 *ptr;
} IntMap;

IntMap *mld_int_map_create(uint32 length)
{
    IntMap *new_map = (IntMap *)malloc(sizeof(IntMap));
    int32 *content = (int32 *)malloc(sizeof(int32) * length);
    new_map->ptr = content;
    new_map->length = length;
    return new_map;
}

void mld_int_map_free(IntMap *int_map)
{
    free(int_map->ptr);
    free(int_map);
    int_map = 0;
}

int main()
{
    IntMap *int_map = mld_int_map_create(10000);
    mld_int_map_free(int_map);
    mld_int_map_free(int_map);
}