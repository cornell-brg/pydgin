//========================================================================
// stdx-DebugUtils.inl
//========================================================================

#include "stdx-ReflectionUtils.h"
#include <iostream>
#include <string>

//------------------------------------------------------------------------
// STDX_DEBUG_CHK
//------------------------------------------------------------------------

#ifdef STDX_DEBUG_OFF
#define STDX_DEBUG_CHK_
#else
#define STDX_DEBUG_CHK_                                                 \
  std::cout << " DEBUG: " << __FILE__ << ":" << __LINE__                \
            << " : " << STDX_SHORT_FUNCTION_NAME << " : "               \
            << "Checkpoint " << std::endl;
#endif

//------------------------------------------------------------------------
// STDX_DEBUG_VAR( var )
//------------------------------------------------------------------------

#ifdef STDX_DEBUG_OFF
#define STDX_DEBUG_VAR_( expr_ )
#else
#define STDX_DEBUG_VAR_( expr_ )                                        \
  std::cout << " DEBUG: " << __FILE__ << ":" << __LINE__                \
            << " : " << STDX_SHORT_FUNCTION_NAME << " : "               \
            << #expr_ << " = " << expr_ << std::endl;
#endif

//------------------------------------------------------------------------
// STDX_DEBUG_MSG( msg )
//------------------------------------------------------------------------

#ifdef STDX_DEBUG_OFF
#define STDX_DEBUG_MSG_( msg_ )
#else
#define STDX_DEBUG_MSG_( msg_ )                                         \
  std::cout << " DEBUG: " << __FILE__ << ":" << __LINE__                \
            << " : " << STDX_SHORT_FUNCTION_NAME << " : "               \
            << msg_ << std::endl;
#endif

