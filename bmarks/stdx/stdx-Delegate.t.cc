//========================================================================
// stdx-Delegate Unit Tests
//========================================================================

#include "stdx-Delegate.h"
#include "stdx-Timer.h"
#include "utst.h"
#include <iostream>
#include <iomanip>
#include <ctime>

//------------------------------------------------------------------------
// Helper Classes
//------------------------------------------------------------------------
// To help test the delegates, we create a common abstract base class
// (IBase) and two subclasses (DerivedA,DerivedB). There are two virtual
// functions (vinc,vdec) which are implemented by both subclases, and
// the subclasses have their own additional non-virtual functions so we
// can test the overhead of various method calls.

class IBase
{
 public:
  virtual ~IBase() { }
  virtual void vinc() = 0;
  virtual void vdec() = 0;
};

class DerivedA : public IBase {

 public:
  DerivedA( int val ) : m_val(val) { }

  __attribute__ ((noinline)) void inc() { m_val++; }
  __attribute__ ((noinline)) void dec() { m_val--; }
  __attribute__ ((noinline)) virtual void vinc() { m_val++; }
  __attribute__ ((noinline)) virtual void vdec() { m_val--; }
  int value() const { return m_val; }

 private:
  int m_val;

};

class DerivedB : public IBase {

 public:
  DerivedB( int val ) : m_val(val) { }
  void inc() { m_val++; }
  void dec() { m_val--; }
  void vinc() { m_val++; }
  void vdec() { m_val--; }
  int value() const { return m_val; }

 private:
  int m_val;

};

//------------------------------------------------------------------------
// TestStdDelegate
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestStdDelegate )
{
  using namespace stdx;

  DerivedA derivedA(1);
  DerivedB derivedB(2);

  StdDelegate incA = mk_delegate<DerivedA,&DerivedA::inc>( &derivedA );
  StdDelegate decA = mk_delegate<DerivedA,&DerivedA::dec>( &derivedA );
  StdDelegate incB = mk_delegate<DerivedB,&DerivedB::inc>( &derivedB );
  StdDelegate decB = mk_delegate<DerivedB,&DerivedB::dec>( &derivedB );

  incA.invoke(); UTST_CHECK_EQ( derivedA.value(), 2 );
  decA.invoke(); UTST_CHECK_EQ( derivedA.value(), 1 );
  incB.invoke(); UTST_CHECK_EQ( derivedB.value(), 3 );
  decB.invoke(); UTST_CHECK_EQ( derivedB.value(), 2 );
}

//------------------------------------------------------------------------
// TestStdDelegateContainer
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestStdDelegateContainer )
{
  using namespace stdx;

  DerivedA derivedA(1);
  DerivedB derivedB(2);

  std::vector<StdDelegate> dVec(4);
  dVec.at(0) = mk_delegate<DerivedA,&DerivedA::inc>( &derivedA );
  dVec.at(1) = mk_delegate<DerivedA,&DerivedA::dec>( &derivedA );
  dVec.at(2) = mk_delegate<DerivedB,&DerivedB::inc>( &derivedB );
  dVec.at(3) = mk_delegate<DerivedB,&DerivedB::dec>( &derivedB );

  dVec.at(0).invoke(); UTST_CHECK_EQ( derivedA.value(), 2 );
  dVec.at(1).invoke(); UTST_CHECK_EQ( derivedA.value(), 1 );
  dVec.at(2).invoke(); UTST_CHECK_EQ( derivedB.value(), 3 );
  dVec.at(3).invoke(); UTST_CHECK_EQ( derivedB.value(), 2 );
}

//------------------------------------------------------------------------
// TestNonStdDelegate
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestNonStdDelegate )
{
  using namespace stdx;

  DerivedA derivedA(1);
  DerivedB derivedB(2);

  NonStdDelegate incA = mk_delegate( &derivedA, &DerivedA::inc );
  NonStdDelegate decA = mk_delegate( &derivedA, &DerivedA::dec );
  NonStdDelegate incB = mk_delegate( &derivedB, &DerivedB::inc );
  NonStdDelegate decB = mk_delegate( &derivedB, &DerivedB::dec );

  incA.invoke(); UTST_CHECK_EQ( derivedA.value(), 2 );
  decA.invoke(); UTST_CHECK_EQ( derivedA.value(), 1 );
  incB.invoke(); UTST_CHECK_EQ( derivedB.value(), 3 );
  decB.invoke(); UTST_CHECK_EQ( derivedB.value(), 2 );
}

//------------------------------------------------------------------------
// TestNonStdDelegateContainer
//------------------------------------------------------------------------

UTST_AUTO_TEST_CASE( TestNonStdDelegateContainer )
{
  using namespace stdx;

  DerivedA derivedA(1);
  DerivedB derivedB(2);

  std::vector<NonStdDelegate> dVec(4);
  dVec.at(0) = mk_delegate( &derivedA, &DerivedA::inc );
  dVec.at(1) = mk_delegate( &derivedA, &DerivedA::dec );
  dVec.at(2) = mk_delegate( &derivedB, &DerivedB::inc );
  dVec.at(3) = mk_delegate( &derivedB, &DerivedB::dec );

  dVec.at(0).invoke(); UTST_CHECK_EQ( derivedA.value(), 2 );
  dVec.at(1).invoke(); UTST_CHECK_EQ( derivedA.value(), 1 );
  dVec.at(2).invoke(); UTST_CHECK_EQ( derivedB.value(), 3 );
  dVec.at(3).invoke(); UTST_CHECK_EQ( derivedB.value(), 2 );
}

//------------------------------------------------------------------------
// PerfComparison
//------------------------------------------------------------------------
// The timing_proxy function is used to estimate how many trials we need
// to get significant timing numbers based on the timer resolution. It
// basically needs to be a proxy for the fasted thing we are timing. In
// this case it will probably be a simple functiona call to A.inc().

void timing_proxy()
{
  DerivedA A(1);
  A.inc();
}

#define DO_TRIAL( descr_, expr_ )                                       \
  timer.start();                                                        \
  for ( int i = 0; i < 10*num_trials ; ++i )                            \
    expr_;                                                              \
  timer.stop();                                                         \
  os << "     - " << std::setw(30) << std::left << descr_ << " : "      \
     << std::setw(20) << std::left << #expr_ << " = "                   \
     << std::fixed << std::setprecision(5) << timer.get_elapsed()       \
     << std::endl;

UTST_AUTO_EXTRA_TEST_CASE( perf, PerfComparison )
{
  using namespace std;
  using namespace stdx;

  // Concrete class

  DerivedA A(1);

  // Pointers to classes

  DerivedA* Ap  = &A;
  IBase*    Abp = &A;

  // Member function pointers

  typedef void (DerivedA::* A_fp_t)();
  A_fp_t A_fp = &DerivedA::inc;

  typedef void (DerivedA::* A_vfp_t)();
  A_vfp_t A_vfp = &DerivedA::vinc;

  typedef void (IBase::* Abp_vfp_t)();
  Abp_vfp_t Abp_vfp = &IBase::vinc;

  // StdDelegates

  StdDelegate sd_A_fp     = mk_delegate<DerivedA,&DerivedA::inc>( Ap );
  StdDelegate sd_A_vfp    = mk_delegate<DerivedA,&DerivedA::vinc>( Ap );
  StdDelegate sd_Abp_vfp  = mk_delegate<IBase,&IBase::vinc>( Abp );

  // NonStdDelegates

  NonStdDelegate nsd_A_fp     = mk_delegate( Ap,  &DerivedA::inc  );
  NonStdDelegate nsd_A_vfp    = mk_delegate( Ap,  &DerivedA::vinc );
  NonStdDelegate nsd_Abp_vfp  = mk_delegate( Abp, &IBase::vinc    );

  // Determine required trials for desired timing precision

  int num_trials = stdx::Timer::estimate_required_trials( &timing_proxy );
  UTST_LOG_VAR( num_trials );

  // Do trials

  utst::TestLog& log = utst::TestLog::instance();
  ostream& os = log.get_log_ostream( utst::TestLog::LogLevel::minimal );
  stdx::Timer timer;

  DO_TRIAL( "mfunc_derived",                 A.inc()              );
  DO_TRIAL( "mfunc_derived_ptr",             Ap->inc()            );

  DO_TRIAL( "vfunc_derived",                 A.vinc()             );
  DO_TRIAL( "vfunc_derived_ptr",             Ap->vinc()           );
  DO_TRIAL( "vfunc_base_ptr",                Abp->vinc()          );

  DO_TRIAL( "mfunc_derived_mfunc_ptr",       (A.*A_fp)()          );
  DO_TRIAL( "mfunc_derived_ptr_mfunc_ptr",   (Ap->*A_fp)()        );
  DO_TRIAL( "vfunc_derived_mfunc_ptr",       (A.*A_vfp)()         );
  DO_TRIAL( "vfunc_derived_ptr_mfunc_ptr",   (Ap->*A_vfp)()       );
  DO_TRIAL( "vfunc_base_ptr_mfunc_ptr",      (Abp->*Abp_vfp)()    );

  DO_TRIAL( "std_delegate_mfunc_derived",    sd_A_fp.invoke()     );
  DO_TRIAL( "std_delegate_vfunc_derived",    sd_A_vfp.invoke()    );
  DO_TRIAL( "std_delegate_vfunc_base",       sd_Abp_vfp.invoke()  );

  DO_TRIAL( "nonstd_delegate_mfunc_derived", nsd_A_fp.invoke()    );
  DO_TRIAL( "nonstd_delegate_vfunc_derived", nsd_A_vfp.invoke()   );
  DO_TRIAL( "nonstd_delegate_vfunc_base",    nsd_Abp_vfp.invoke() );
}

//------------------------------------------------------------------------
// Main
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  utst::auto_command_line_driver( argc, argv );
}

