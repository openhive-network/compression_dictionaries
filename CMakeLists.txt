SET(ZSTD_DICTIONARY_C_FILES)

FIND_PROGRAM(RESOURCE_COMPILER xxd REQUIRED)

set(DICTIONARY_DECLARATIONS "#include <hive/chain/raw_compression_dictionaries.hpp>\nextern \"C\"\n{")
set(MAP_INITIALIZATION "namespace hive { namespace chain {\n\
const std::map<uint8_t, raw_dictionary_info> raw_dictionaries = {")

FOREACH(DICTIONARY_NUM RANGE 90)
  STRING(LENGTH "${DICTIONARY_NUM}" DICTIONARY_NUM_LEN)
  MATH(EXPR LEADING_ZEROS_NEEDED "2 - ${DICTIONARY_NUM_LEN}")
  SET(DICTIONARY_NUM_STRING "${DICTIONARY_NUM}")
  FOREACH(DUMMY RANGE ${LEADING_ZEROS_NEEDED})
    SET(DICTIONARY_NUM_STRING "0${DICTIONARY_NUM_STRING}")
  ENDFOREACH()
  SET(ZSTD_DICTIONARY_SOURCE_FILENAME "${DICTIONARY_NUM_STRING}M.dict.zst")
  SET(ZSTD_DICTIONARY_C_FILENAME "${DICTIONARY_NUM_STRING}M.c")
  LIST(APPEND ZSTD_DICTIONARY_C_FILES ${ZSTD_DICTIONARY_C_FILENAME})
  ADD_CUSTOM_COMMAND(OUTPUT ${ZSTD_DICTIONARY_C_FILENAME}
                     DEPENDS ${ZSTD_DICTIONARY_SOURCE_FILENAME}
                     WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                     COMMAND ${RESOURCE_COMPILER} -i ${ZSTD_DICTIONARY_SOURCE_FILENAME} ${CMAKE_CURRENT_BINARY_DIR}/${ZSTD_DICTIONARY_C_FILENAME}
                     COMMENT "Compiling ${ZSTD_DICTIONARY_SOURCE_FILENAME} to .c")

  set(DICTIONARY_DECLARATIONS "${DICTIONARY_DECLARATIONS}\n\
  extern unsigned char __${DICTIONARY_NUM_STRING}M_dict_zst[];\n\
  extern unsigned __${DICTIONARY_NUM_STRING}M_dict_zst_len;")
  set(MAP_INITIALIZATION "${MAP_INITIALIZATION}\n\
  {${DICTIONARY_NUM}, {(const void*)__${DICTIONARY_NUM_STRING}M_dict_zst, (unsigned)__${DICTIONARY_NUM_STRING}M_dict_zst_len}},")
ENDFOREACH()

set(DICTIONARY_DECLARATIONS "${DICTIONARY_DECLARATIONS}\n} // end extern \"C\"")
set(MAP_INITIALIZATION "${MAP_INITIALIZATION}\n};\n} } // end namespace hive::chain")

set(CMAKE_CONFIGURABLE_FILE_CONTENT "${DICTIONARY_DECLARATIONS}\n${MAP_INITIALIZATION}")
configure_file("${CMAKE_ROOT}/Modules/CMakeConfigurableFile.in" "${CMAKE_CURRENT_BINARY_DIR}/compression_dictionaries.cpp" @ONLY)
unset(CMAKE_CONFIGURABLE_FILE_CONTENT)

add_library( hive_chain_compression_dictionaries
             ${ZSTD_DICTIONARY_C_FILES}
             "${CMAKE_CURRENT_BINARY_DIR}/compression_dictionaries.cpp" )
target_include_directories( hive_chain_compression_dictionaries PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../include" )
if( CLANG_TIDY_EXE )
   set_target_properties(
      hive_chain_compression_dictionaries PROPERTIES
      CXX_CLANG_TIDY "${DO_CLANG_TIDY}"
   )
endif( CLANG_TIDY_EXE )

INSTALL( TARGETS
   hive_chain_compression_dictionaries

   RUNTIME DESTINATION bin
   LIBRARY DESTINATION lib
   ARCHIVE DESTINATION lib
)
