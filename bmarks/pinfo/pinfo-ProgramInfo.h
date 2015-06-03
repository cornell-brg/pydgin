//========================================================================
// pinfo-ProgramInfo.h : Program argument and module information repo
//========================================================================
// See 'pinfo-uguide.txt' for more information about using the program
// info subproject.

#ifndef PINFO_PROGRAM_INFO_H
#define PINFO_PROGRAM_INFO_H

#include <iostream>
#include <fstream>
#include <string>
#include <map>

namespace  pinfo {

  class ProgramInfo {
   public:

    //--------------------------------------------------------------------
    // Constructors/Destructors
    //--------------------------------------------------------------------

    ProgramInfo();
    ~ProgramInfo();

    //--------------------------------------------------------------------
    // Specify module information and arguments
    //--------------------------------------------------------------------

    // Add a module to the list of known modules
    void add_module( const char* name, const char* version );

    // Add an arg to the list of possible args
    void add_arg( const char* arg, const char* name, const char* def,
                  const char* comment = NULL );

    // Change already parsed arg - return old value or NULL if not found
    const char* set_value( const char* arg, const char* value );

    //--------------------------------------------------------------------
    // Parse arguments
    //--------------------------------------------------------------------

    // Parse the command line args, giving usage messages if necessary
    int parse_args( int argc, char **argv );

    //--------------------------------------------------------------------
    // Extract arguments
    //--------------------------------------------------------------------

    // Get the string corresponding to an arg
    const char* get_string( const char* arg );

    // Interpret arg as a stream name and open that stream
    std::ostream& get_logstream( const char* arg );

    // Interpret arg as a hex or decimal long and return value
    long get_long( const char* arg );

    // Interpret arg as a hex or decimal unsigned long and return value
    unsigned long get_ulong( const char* arg );

    // Interpret arg as a binary value - "0" or "1"
    int get_binary( const char* arg);

    // Interpret an arg as a double precision floating point value
    double get_double( const char* arg );

    // Check for the presence of a flag arg (no value)
    int get_flag( const char* arg );

    //--------------------------------------------------------------------
    // Get information about program and modules
    //--------------------------------------------------------------------

    // Show names and versions of all modules
    void show_version();

    // Show usage message including all registered args
    void show_usage( int error );

    // Return the program name (basename of argv[0])
    const char* program_name();

    //--------------------------------------------------------------------
    // Error and warning streams
    //--------------------------------------------------------------------

    // Print an error message
    std::ostream& error( const char* module = NULL );

    // Print a warning message
    std::ostream& warning( const char* module = NULL );

    //--------------------------------------------------------------------
    // Access global instance
    //--------------------------------------------------------------------

    static ProgramInfo& instance();

   private:

    //--------------------------------------------------------------------
    // Private data
    //--------------------------------------------------------------------

    enum
    {
      MAX_MODULES  = 20,
      MAX_ARGS     = 50,
      MAX_POSARGS  = 10,
      MAX_LOGFILES = 10
    };

    enum
    {
      ARG_WIDTH = 10,
      VAL_WIDTH = 20
    };

    // Structure for storing arg information
    struct Arg
    {
      const char* arg;        // Arg name
      const char* name;       // Name of arg for usage message
      const char* def;        // Default value
      const char* value;      // Actual value
      const char* descrip;    // Description
    };

    // Structure for storing module information
    struct Module
    {
      const char* name;       // Module name
      const char* version;    // Module version
    };

    // List of args we know about
    Arg m_args[MAX_ARGS];

    // Number of args we know about
    int m_arg_count;

    // List of modules
    Module m_modules[MAX_MODULES];

    // Number of modules
    int m_module_count;

    // List of files used to log data
    std::ofstream* m_logfiles[MAX_LOGFILES];

    // Count of log files
    int m_logfile_count;

    // Map from file name to ofstream for duplicate logfiles
    std::map<std::string,std::ofstream*> m_logfile_map;

    // Pointer to program name
    const char* m_progname;

    // Warning and error output
    std::ostream* m_warn_out;
    std::ostream* m_err_out;

    int m_warn_max;
    int m_err_max;
    int m_warn_count;
    int m_err_count;

  };

}

#endif /* PINFO_PROGRAM_INFO_H */

