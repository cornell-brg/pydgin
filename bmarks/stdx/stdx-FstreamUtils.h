//========================================================================
// stdx-FstreamUtils : Utilities for file streams
//========================================================================
// Using the built-in fstreams is a little frustrating for a couple of
// reasons. We cannot use an STL string as file name and instead we have
// to convert the file name into a character array. We always have to
// check if opening the file failed and if so we need to print out why.
// Finally, it's a little annoying to transparently switch between
// standard input (or output) and a file based on the file name. To
// illustrate these issues, here is a little program which takes a file
// name as a command line argument and echos it to standard out. If the
// given file name is "-" then the program awaits input from standard
// in.
//
//  #include <iostream>
//  #include <fstream>
//  #include <string>
//  #include <errno.h>
//
//  int main( int argc, char* argv[] )
//  {
//    std::string in_fname(argv[1]);
//    bool use_stdin = (in_fname == "-");
//
//    std::istream* is;
//    if ( use_stdin )
//      is = &std::cin;
//    else {
//      std::cout << "file" << std::endl;
//      is = new std::ifstream( in_fname.c_str(), std::ios_base::in );
//      if ( is->fail() ) {
//        std::cout << "Error: " << in_fname << " - "
//                  << std::strerror(errno) << std::endl;
//        exit(1);
//      }
//    }
//
//    std::string buf;
//    while ( (*is) >> buf )
//      std::cout << buf;
//
//    if ( !use_stdin )
//      delete is;
//  }
//
// Notice the boiler plate error checking code and the complexities of
// handling the switch between standard input and file input. The
// classes contained in this header can do all this for you. Here is the
// same example using the DefaultStdinFstream class:
//
//  #include "stdx-FstreamUtils.h"
//  #include <iostream>
//
//  int main( int argc, char* argv[] )
//  {
//    stdx::DefaultStdinFstream fin(argv[1]);
//
//    std::string buf;
//    while ( fin >> buf )
//      std::cout << buf;
//  }
//
// The DefaultStdinFstream class will throw an ECannotOpenFile exception
// if it has trouble and it will include the system error message in the
// exception. Plus it automatically handles switching between standard
// input and file input if you specify a file name of "-". And the file
// name can be either a character array or an STL string.
//

#ifndef STDX_FSTREAM_UTILS_H
#define STDX_FSTREAM_UTILS_H

#include "stdx-Exception.h"
#include <fstream>

namespace stdx {

  //----------------------------------------------------------------------
  // ECannotOpenFile
  //----------------------------------------------------------------------
  // Exception thrown if there is an error when opening the file.
  // Exception includes some information on why the file could not be
  // opened.

  struct ECannotOpenFile : public stdx::Exception { };

  //----------------------------------------------------------------------
  // CheckedInputFstream
  //----------------------------------------------------------------------
  // This class is a simple wrapper for a ifstream which will check to
  // see if the constructed ifstream is valid. If not, then the
  // constructor throws an ECannotOpenFile exception.

  class CheckedInputFstream : public std::ifstream {
   public :

    CheckedInputFstream();
    CheckedInputFstream( const std::string& name,
                         std::ios_base::openmode m = std::ios_base::in );

    ~CheckedInputFstream();

    void open( const std::string& name,
               std::ios_base::openmode m = std::ios_base::in );
  };

  //----------------------------------------------------------------------
  // DefaultStdinFstream
  //----------------------------------------------------------------------
  // This class is a simple wrapper for a istream. If the given file
  // name is "-" then the resulting istream will be connected to
  // standard in. Otherwise the file with the given file name is opened
  // and if there is an error we throw an ECannotOpenFile exception.

  class DefaultStdinFstream : public std::istream {
   public:

    DefaultStdinFstream();
    DefaultStdinFstream( const std::string& name );
    ~DefaultStdinFstream();

    void open( const std::string& name );

   private:
    std::ifstream* m_is_ptr;
  };

  //----------------------------------------------------------------------
  // CheckedInOutFstream
  //----------------------------------------------------------------------
  // This class is a simple wrapper for a iofstream which will check to
  // see if the constructed ifstream is valid. If not, then the
  // constructor throws an ECannotOpenFile exception.

  class CheckedInOutFstream : public std::fstream {

   public :

    CheckedInOutFstream();
    CheckedInOutFstream( const std::string& name,
                         std::ios_base::openmode m
                           = std::ios_base::in | std::ios_base::out );

    ~CheckedInOutFstream();

    void open( const std::string& name,
               std::ios_base::openmode m
                 = std::ios_base::in | std::ios_base::out );
  };

  //----------------------------------------------------------------------
  // CheckedOutputFstream
  //----------------------------------------------------------------------
  // This class is a simple wrapper for a ofstream which will check to
  // see if the constructed ofstream is valid. If not, then the
  // constructor throws an ECannotOpenFile exception.

  class CheckedOutputFstream : public std::ofstream {
   public :

    CheckedOutputFstream();
    CheckedOutputFstream( const std::string& name,
                          std::ios_base::openmode m = std::ios_base::out );

    ~CheckedOutputFstream();

    void open( const std::string& name,
               std::ios_base::openmode m = std::ios_base::out );
  };

  //----------------------------------------------------------------------
  // DefaultStdoutFstream
  //----------------------------------------------------------------------
  // This class is a simple wrapper for a ostream. If the given file
  // name is "-" then the resulting ostream will be connected to
  // standard out. Otherwise the file with the given file name is opened
  // and if there is an error an ECannotOpenFile exception is thrown.

  class DefaultStdoutFstream : public std::ostream {
   public:

    DefaultStdoutFstream();
    DefaultStdoutFstream( const std::string& name );
    ~DefaultStdoutFstream();

    void open( const std::string& name );

   private:
    std::ofstream* m_os_ptr;
  };

}

#endif /* STDX_FSTREAM_UTILS_H */

