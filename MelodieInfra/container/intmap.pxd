cdef extern from "mld_int_map.c":
    """
    #define _validate_key(int_map, key)  (0 <= key && key < int_map->length)
    #define _mld_int_map_get(int_map, key) (_validate_key(int_map, key)? int_map->ptr[key]: -1)
    #define _mld_int_map_set(int_map, key, value) (if(_validate_key(int_map, key)){int_map->ptr[key] = value;})
    """
    ctypedef int int32;
    ctypedef unsigned int uint32;
    ctypedef struct IntMap:
        uint32 length;
        int32 *ptr;
    
    IntMap* mld_int_map_create(int32 length)
    void mld_int_map_free(IntMap *int_map)
    # int32 mld_int_map_get(IntMap *int_map, uint32 key)
    void mld_int_map_set "_mld_int_map_get" (IntMap *int_map, uint32 key, int32 value)
    int32 mld_int_map_get "_mld_int_map_get" (IntMap *int_map, uint32 key)

    bint mld_key_in_int_map "_validate_key" (IntMap *int_map, uint32 key)