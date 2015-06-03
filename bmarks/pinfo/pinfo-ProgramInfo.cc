//========================================================================
// pinfo-ProgramInfo.cc
//========================================================================

#include "pinfo-ProgramInfo.h"

#include <cstring>
#include <cstdlib>
#include <cassert>
#include <iomanip>
#include <iostream>

namespace pinfo {

  //----------------------------------------------------------------------
  // Constructors/Destructors
  //----------------------------------------------------------------------

  ProgramInfo::ProgramInfo()
   : m_arg_count(0),
     m_module_count(0),
     m_logfile_count(0),
     m_warn_out(&std::cerr),
     m_err_out(&std::cerr),
     m_warn_max(1000),
     m_err_max(1000),
     m_warn_count(0),
     m_err_count(0)
  {
    add_arg("-h", NULL, NULL, "Show this usage message");
    add_arg("-v", NULL, NULL, "Show program version information");
    add_arg("--warn-out", "logfile", "std::cerr", "Destination for warning messages");
    add_arg("--warn-limit", "integer", "1000", "Maximum number of warnings before exiting");
    add_arg("--err-out", "logfile", "std::cerr", "Destination for error messages");
    add_arg("--err-limit", "integer", "1000", "Maximum number of errors before exiting");
  }

  ProgramInfo::~ProgramInfo()
  {
    for ( int i = 0; i < m_logfile_count; i++ ) {
      (*m_logfiles[i]).close();
      delete m_logfiles[i];
    }
  }

  //----------------------------------------------------------------------
  // add_module
  //----------------------------------------------------------------------

  void ProgramInfo::add_module( const char* name, const char* version )
  {
    assert( m_module_count < MAX_MODULES );
    m_modules[m_module_count].name    = name;
    m_modules[m_module_count].version = version;
    m_module_count++;
  }

  //----------------------------------------------------------------------
  // add_arg
  //----------------------------------------------------------------------

  void ProgramInfo::add_arg( const char* arg, const char* name,
                             const char* def, const char* descrip )
  {
    assert( arg != NULL );
    assert( ( *arg == '-' )
                 || ( (*arg == '*') && (*(arg+1) == '\0') )
                 || ( (*arg >= '1') && (*arg <= '9') && (*(arg+1) == '\0') ));

    // Look for arg with this name already - if there is one, change it

    for ( int i = 0; i < m_arg_count; i++ ) {
      if ( strcmp( arg, m_args[i].arg ) == 0 ) {
        if ( def != NULL )
          m_args[i].def = def;
        if ( name != NULL )
          m_args[i].name = name;
        if ( descrip != NULL )
          m_args[i].descrip = descrip;
        return;
      }
    }

    // Argument is a new one - add it to end of list

    assert( m_arg_count < MAX_ARGS );
    m_args[m_arg_count].arg   = arg;
    m_args[m_arg_count].name  = name;
    m_args[m_arg_count].value = NULL;

    // Flags must have non-null default

    if ( name == NULL )
      m_args[m_arg_count].def = "";
    else
      m_args[m_arg_count].def = def;

    m_args[m_arg_count].descrip = descrip;
    m_arg_count++;
  }

  //----------------------------------------------------------------------
  // set_value
  //----------------------------------------------------------------------

  const char* ProgramInfo::set_value( const char* arg, const char* value )
  {
    assert( arg != NULL );

    const char* old = NULL;
    for ( int i = 0; i < m_arg_count; i++ ) {
      if ( strcmp( m_args[i].arg, arg ) == 0 ) {
        old = m_args[i].value;
        m_args[i].value = value;
      }
    }

    return old;
  }

  //----------------------------------------------------------------------
  // parse_args
  //----------------------------------------------------------------------

  int ProgramInfo::parse_args( int argc, char** argv )
  {
    // Work out name of program from argv[0];

    m_progname = argv[0];
    const char* s = m_progname;
    while ( *s ) {
      if ( *s++ == '/' )
        m_progname = s;
    }

    // Fill in default values for arguments

    int wild_arg = 0;      // 1 if okay to return unused arguments
    int argv_next = argc;  // Return value - next argv element unused
    for ( int i = 0; i < m_arg_count; i++ ) {
      m_args[i].value = m_args[i].def;
      if (*(m_args[i].arg) == '*' )
        wild_arg = 1;
    }

    // Parse arguments

    int current_posarg = '1'; // Current positional argument number
    int arg_found;            // 1 if we found arg we are looking for

    for ( int i = 1; i < argc; i++ ) {
      const char* arg = argv[i];

      if ( strcmp( arg, "-v" ) == 0 ) {
        show_version();
        exit(0);
      }
      else if ( strcmp( arg, "-h") == 0 ) {
        show_usage(0);
        exit(0);
      }

      if ( *arg == '-' ) {
        arg_found = 0;
        for ( int j = 0; j < m_arg_count; j++ ) {

          if ( strcmp( m_args[j].arg, arg ) == 0 ) {
            arg_found = 1;

            if ( m_args[j].name == NULL ) {
              m_args[j].value = arg; // Flags value is their own name
              break;
            }
            else {

              if ( ++i < argc ) {
                m_args[j].value = argv[i];
                break;
              }
              else {
                error() << "must provide value for argument "
                        << arg << " <" << m_args[j].name << ">\n";
                show_usage(1);
              }

            }
          }

        }

        if ( !arg_found ) {
          error() << "unknown argument " << arg << "\n";
          show_usage(1);
        }

      }

      // arg is not -something

      else {
        arg_found = 0;

        for ( int j = 0; j < m_arg_count; j++ ) {
          if ( *(m_args[j].arg) == current_posarg ) {
            arg_found = 1;
            m_args[j].value = argv[i];
            current_posarg++;
            break;
          }
        }

        if ( !arg_found ) {
          if ( wild_arg ) {
            argv_next = i;
            break;
          }
          else {
            // Give an error on unknown arguments if they are not allowed
            show_usage(1);
          }
        }
      }
    }

    // Check there are no arguments without values

    for ( int i = 0; i < m_arg_count; i++ ) {

      if ( (m_args[i].value == NULL) && (*(m_args[i].arg) != '*') ) {
        error() << "must provide value for argument "
                << m_args[i].arg << " <" << m_args[i].name << ">\n";
        show_usage(1);
      }
    }

    // Setup warning and output stream pointers

    m_warn_out = &get_logstream("--warn-out");
    m_err_out  = &get_logstream("--err-out");
    m_warn_max = get_ulong("--warn-limit");
    m_err_max  = get_ulong("--err-limit");

    // Return location of the first unmatched arg (argc if no wild args)

    return argv_next;
  }

  //----------------------------------------------------------------------
  // get_string
  //----------------------------------------------------------------------

  const char* ProgramInfo::get_string( const char* arg ) 
  {
    assert( arg != NULL );

    for ( int i = 0; i < m_arg_count; i++ ) {
      if ( strcmp( m_args[i].arg, arg ) == 0 ) {
        if ( m_args[i].value != NULL )
          return m_args[i].value;
        else {
          assert( m_args[i].def != NULL );
          return m_args[i].def;
        }
      }
    }

    // We should get an error before here if arg does not exist

    error() << "INTERNAL ERROR - tried to get value of unknown argument "
            << arg << "\n";

    assert(0);
    return NULL;
  }

  //----------------------------------------------------------------------
  // get_logstream
  //----------------------------------------------------------------------

  std::ostream& ProgramInfo::get_logstream( const char* arg )
  {
    assert( arg != NULL );
    const char* s = get_string(arg);
    assert( s != NULL );

    if ( strcmp( s, "-" ) == 0 )
      return std::cout;

    else if ( strcmp( s, "std::cout" ) == 0 )
      return std::cout;

    else if ( strcmp( s, "std::cerr" ) == 0 )
      return std::cerr;

    else if ( m_logfile_map.find(s) != m_logfile_map.end() )
      return static_cast<std::ostream&>(*m_logfile_map[s]);

    else {
      assert( m_logfile_count < MAX_LOGFILES );
      std::ofstream* f = new std::ofstream(s); // Open log file
      if ( !f ) {
        error() << "failed to open file " << s << " for output\n";
        exit(1);
      }
      m_logfile_map[s] = f;
      return static_cast<std::ostream&>(*f);
    }
  }

  //----------------------------------------------------------------------
  // get_long
  //----------------------------------------------------------------------

  long ProgramInfo::get_long( const char* arg )
  {
    assert( arg != NULL );
    const char* s = get_string(arg);
    assert( s != NULL );

    const char* s2; // End of number read
    long value = strtol( s, (char**) &s2, 0 );
    if ( s2 == s ) {
      error() << "bad value for argument " << arg
              << " - must be a decimal/octal/hex number\n";
      exit(1);
    }
    return value;
  }

  //----------------------------------------------------------------------
  // get_ulong
  //----------------------------------------------------------------------

  unsigned long ProgramInfo::get_ulong( const char* arg )
  {
    assert( arg != NULL );
    const char* s = get_string(arg);
    assert( s != NULL );

    const char* s2; // End of number read
    unsigned long value = strtoul( s, (char**) &s2, 0 );
    if ( s2 == s ) {
      error() << "bad value for argument " << arg
              << " - must be a decimal/octal/hex number\n";
      exit(1);
    }
    return value;
  }

  //----------------------------------------------------------------------
  // get_binary
  //----------------------------------------------------------------------

  int ProgramInfo::get_binary( const char* arg )
  {
    assert( arg != NULL );
    const char* str = get_string(arg);
    assert( str != NULL );

    int value;
    if ( strcmp( str, "0" ) == 0 )
      value = 0;

    else if ( strcmp( str, "1") == 0 )
      value = 1;

    else {
      error() << "bad value for " << arg << " - must be 0 or 1\n";
      exit(1);
    }

    return value;
  }

  //----------------------------------------------------------------------
  // get_double
  //----------------------------------------------------------------------

  double ProgramInfo::get_double( const char* arg )
  {
    assert( arg != NULL );
    const char* s = get_string(arg);
    assert(s!=NULL);

    const char* s2; // End of number read
    double value = strtod( s, (char**) &s2 );
    if ( s2 == s ) {
      error() << "bad value for argument " << arg
              << " - must be a floating point number\n";
      exit(1);
    }

    return value;
  }

  //----------------------------------------------------------------------
  // get_flag
  //----------------------------------------------------------------------

  int ProgramInfo::get_flag( const char* arg )
  {
    assert( arg != NULL );
    const char* str = get_string(arg);

    if ( strcmp( arg, str ) == 0 )
      return 1;
    else
      return 0;
  }

  //----------------------------------------------------------------------
  // show_version
  //----------------------------------------------------------------------

  void ProgramInfo::show_version()
  {
    std::cerr << "*** " << program_name() << " ***\n";
    for ( int i = 0; i < m_module_count; i++ )
      std::cerr << m_modules[i].name << ": " << m_modules[i].version << "\n";
  }

  //----------------------------------------------------------------------
  // show_usage
  //----------------------------------------------------------------------

  void ProgramInfo::show_usage( int error )
  {
    const int COMMENT_COLUMN = 32;  // Where usage comments start

    const char* pos_names[MAX_POSARGS];    // Names for pos args
    const char* pos_defaults[MAX_POSARGS]; // Defaults for pos args

    for ( int i = 0; i < MAX_POSARGS; i++ ) {
      pos_names[i] = NULL;
      pos_defaults[i] = NULL;
    }

    int options = 0;                // 1 when possible optional args
    const char* rest_name = NULL;   // Name for rest of command
    char pos_no;                    // Current positional argument

    for ( int i = 0; i < m_arg_count; i++ ) {

      if (*(m_args[i].arg)=='-')
        options = 1;

      else if (*(m_args[i].arg)=='*')
        rest_name = m_args[i].name;

      else {
        pos_no = *(m_args[i].arg);
        assert(pos_no >= '0' && pos_no <= ('0' + MAX_POSARGS));
        pos_no -= '0';
        pos_names[static_cast<int>(pos_no)] = m_args[i].name;
        pos_defaults[static_cast<int>(pos_no)] = m_args[i].def;
      }
    }

    std::cerr << "Usage: " << program_name();
    if ( options )
        std::cerr << " [<options>]";

    for ( int i = 0; i < MAX_POSARGS; i++ ) {
      if ( pos_names[i] != NULL ) {

        if ( pos_defaults[i] != NULL )
          std::cerr << " [<" << pos_names[i] << "=" << pos_defaults[i] << ">]";
        else
          std::cerr << " <" << pos_names[i] << ">";
      }
    }

    if ( rest_name != NULL )
        std::cerr << " " << rest_name;
    std::cerr << "\n";

    int width;
    if ( options ) {
      std::cerr << "where <options> is zero or more of:\n";
      for ( int i = 0; i < m_arg_count; i++ ) {

        if ( *(m_args[i].arg) == '-' ) {

          std::cerr << "  " << m_args[i].arg;
          width = 2 + strlen( m_args[i].arg );
          if ( m_args[i].name != NULL ) {

            std::cerr << " <" << m_args[i].name;
            if ( m_args[i].def != NULL ) {
              std::cerr << "=" << m_args[i].def;
              width += strlen( m_args[i].def ) + 1;
            }

            std::cerr << ">";
            width += strlen( m_args[i].name ) + 3;
          }

          if ( m_args[i].descrip != NULL ) {
            for ( ; width < COMMENT_COLUMN; width++ )
              std::cerr << ' ';
            std::cerr << "   " << m_args[i].descrip;
          }

          std::cerr << "\n";
        }
      }
    }

    exit(error);
  }

  //----------------------------------------------------------------------
  // program_name
  //----------------------------------------------------------------------

  const char* ProgramInfo::program_name()
  {
    return m_progname;
  }

  //----------------------------------------------------------------------
  // error
  //----------------------------------------------------------------------

  std::ostream& ProgramInfo::error( const char* module )
  {
    *m_err_out << m_progname;

    m_err_count++;
    if ( m_err_count > m_err_max ) {
      *m_err_out << ": ERROR - reached --err-limit" << std::endl;
      exit(1);
    }

    if ( module != NULL )
      *m_err_out << "(" << module << ")";
    *m_err_out << ": ERROR - ";

    return *m_err_out;
  }

  //----------------------------------------------------------------------
  // warning
  //----------------------------------------------------------------------

  std::ostream& ProgramInfo::warning( const char* module )
  {
    *m_warn_out << m_progname;

    m_warn_count++;
    if ( m_warn_count > m_warn_max ) {
      *m_err_out << ": ERROR - reached --warn-limit" << std::endl;
      exit(1);
    }

    if ( module != NULL )
      *m_warn_out << "(" << module << ")";
    *m_warn_out << ": WARNING - ";
    return *m_warn_out;
  }

  //----------------------------------------------------------------------
  // instance
  //----------------------------------------------------------------------

  ProgramInfo& ProgramInfo::instance()
  {
    static ProgramInfo s_instance;
    return s_instance;
  }

}

