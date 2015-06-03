//========================================================================
// stdx-FstreamUtils.cc
//========================================================================

#include "stdx-FstreamUtils.h"
#include <iostream>
#include <cstring>
#include <cerrno>

namespace stdx {

  //----------------------------------------------------------------------
  // CheckedInputFstream
  //----------------------------------------------------------------------

  CheckedInputFstream::CheckedInputFstream()
  { }

  CheckedInputFstream::CheckedInputFstream( const std::string& name,
                                            std::ios_base::openmode mode )
  {
    open( name, mode );
  }

  CheckedInputFstream::~CheckedInputFstream()
  {
    close();
  }

  void CheckedInputFstream::open( const std::string& name,
                                  std::ios_base::openmode mode )
  {
    std::ifstream::open( name.c_str(), mode | std::ios_base::in );
    if ( fail() )
      STDX_THROW( stdx::ECannotOpenFile,
       "Error opening file " << name << " - " << std::strerror(errno) );
  }

  //----------------------------------------------------------------------
  // DefaultStdinFstream
  //----------------------------------------------------------------------

  DefaultStdinFstream::DefaultStdinFstream()
   : m_is_ptr(0)
  { }

  DefaultStdinFstream::DefaultStdinFstream( const std::string& name )
   : std::istream( std::cin.rdbuf() ), m_is_ptr(0)
  {
    open( name );
  }

  DefaultStdinFstream::~DefaultStdinFstream()
  {
    if ( m_is_ptr != 0 ) {
      m_is_ptr->close();
      delete m_is_ptr;
    }
  }

  void DefaultStdinFstream::open( const std::string& name )
  {
    if ( name != "-" ) {
      m_is_ptr = new stdx::CheckedInputFstream(name);
      rdbuf( m_is_ptr->rdbuf() );
    }
  }

  //----------------------------------------------------------------------
  // CheckedInOutFstream::CheckedInOutFstream()
  //----------------------------------------------------------------------

  CheckedInOutFstream::CheckedInOutFstream()
  { }

  CheckedInOutFstream::CheckedInOutFstream( const std::string& name,
                                            std::ios_base::openmode mode )
  {
    open( name, mode );
  }

  CheckedInOutFstream::~CheckedInOutFstream()
  {
    close();
  }

  void CheckedInOutFstream::open( const std::string& name,
                                  std::ios_base::openmode mode )
  {
    std::fstream::open( name.c_str(),
                        mode|std::ios_base::in|std::ios_base::out );
    if ( fail() )
      STDX_THROW( stdx::ECannotOpenFile,
       "Error opening file " << name << " - " << std::strerror(errno) );
  }

  //----------------------------------------------------------------------
  // CheckedOutputFstream
  //----------------------------------------------------------------------

  CheckedOutputFstream::CheckedOutputFstream()
  { }

  CheckedOutputFstream::CheckedOutputFstream( const std::string& name,
                                              std::ios_base::openmode mode )
  {
    open( name, mode );
  }

  CheckedOutputFstream::~CheckedOutputFstream()
  {
    close();
  }

  void CheckedOutputFstream::open( const std::string& name,
                                   std::ios_base::openmode mode )
  {
    std::ofstream::open( name.c_str(), mode | std::ios_base::out );
    if ( fail() )
      STDX_THROW( stdx::ECannotOpenFile,
       "Error opening file " << name << " - " << std::strerror(errno) );
  }

  //----------------------------------------------------------------------
  // DefaultStdoutFstream
  //----------------------------------------------------------------------

  DefaultStdoutFstream::DefaultStdoutFstream()
  { }

  DefaultStdoutFstream::DefaultStdoutFstream( const std::string& name )
   : std::ostream( std::cout.rdbuf() ), m_os_ptr(0)
  {
    open( name );
  }

  DefaultStdoutFstream::~DefaultStdoutFstream()
  {
    if ( m_os_ptr != 0 ) {
      m_os_ptr->close();
      delete m_os_ptr;
    }
  }

  void DefaultStdoutFstream::open( const std::string& name )
  {
    if ( name != "-" ) {
      m_os_ptr = new stdx::CheckedOutputFstream(name);
      rdbuf( m_os_ptr->rdbuf() );
    }
  }

}

