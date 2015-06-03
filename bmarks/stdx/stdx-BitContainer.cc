//========================================================================
// stdx-BitContainer.cc
//========================================================================

#include "stdx-BitContainer.h"
#include <sstream>
#include <iomanip>
#include "stdx-DebugUtils.h"

namespace stdx {
namespace details {

  //----------------------------------------------------------------------
  // bits_to_str
  //----------------------------------------------------------------------
  // Assumes that the high order bits are already reset. Also assumes
  // that the numer of bits is not more than the capacity of the bit
  // word container.

  void bits_to_str( const BitWord bits[], int num_bits, std::string* str )
  {
    const int num_digits_per_word = g_bit_word_sz / 4;
    int msb_word = num_bits / g_bit_word_sz;

    // Convert most significant word into a hex string

    std::ostringstream ost;
    ost << std::hex << std::setw(num_digits_per_word)
        << std::setfill('0') << bits[msb_word];
    std::string msw_str = ost.str();
    ost.str("");

    // Truncate hex string according to number of bits in most
    // significant word, and then append to running output stream

    int num_valid_digits_in_msw = ((num_bits % g_bit_word_sz)+3)/4;

    ost << "0x";
    ost << msw_str.substr( num_digits_per_word - num_valid_digits_in_msw,
                           num_valid_digits_in_msw );

    // Append the rest of the words

    for ( int idx = msb_word-1; idx >= 0; idx-- )
      ost << std::hex << std::setw(num_digits_per_word)
          << std::setfill('0') << bits[idx];

    *str = ost.str();
  }

  //----------------------------------------------------------------------
  // bits_from_str
  //----------------------------------------------------------------------
  // Assumes that target bit words are already reset. We take the same
  // approach for both binary and hex input strings. Basically we scan
  // the input characters from the right to left (ie. lsb to msb), and
  // for each digit we shift and or into the approriate word of the
  // givien bit word container.

  void bits_from_str( BitWord bits[], int num_bits,
                      const std::string& str )
  {

    // Binary string

    if ( (str.size() > 2) && str.substr(0,2) == "0b" ) {

      int word_idx = 0;
      int bit_idx  = 0;

      for ( int i = str.length()-1; i >= 2; i-- ) {

        if ( (str[i] != '_') && (bit_idx >= num_bits) )
          STDX_THROW( BitContainerExceptions::EInvalidStringConversion,
                      "Bit string \"" << str << "\" has more bits than "
                        << "bit container (" << num_bits << ")" );

        if ( (str[i] == '1') || (str[i] == '0') ) {
          if ( str[i] == '1' )
            bits[word_idx] |= (g_bit_word_1 << (bit_idx % g_bit_word_sz));

          bit_idx++;
          if ( (bit_idx % g_bit_word_sz) == 0 )
            word_idx++;

        }
        else if ( str[i] != '_' )
          STDX_THROW( BitContainerExceptions::EInvalidStringConversion,
                      "Could not parse bit " << i << " of " << str );

      }
    }

    // Hex string

    else if ( (str.size() > 2) && str.substr(0,2) == "0x" ) {

      int  word_idx    = 0;
      char digit_str[] = "0";
      int  digit_idx   = 0;

      for ( int i = str.length()-1; i >= 2; i-- ) {

        if ( (str[i] != '_') && (digit_idx*4 >= num_bits) )
          STDX_THROW( BitContainerExceptions::EInvalidStringConversion,
                      "Bit string \"" << str << "\" has more bits than "
                        << "bit container (" << num_bits << ")" );

        if ( std::isxdigit(str[i]) ) {
          digit_str[0] = str[i];
          int digit = strtol(digit_str,NULL,16);

          // Make sure last digit doesn't have too many "one" bits

          int bits_left = num_bits - digit_idx*4;
          if ( bits_left < 4 ) {

            bool too_many_bits
              =    ( (bits_left == 1) && (digit > 1) )
                || ( (bits_left == 2) && (digit > 3) )
                || ( (bits_left == 3) && (digit > 7) );

            if ( too_many_bits )
              STDX_THROW( BitContainerExceptions::EInvalidStringConversion,
                          "Bit string \"" << str << "\" has more bits than"
                          << " bit container (" << num_bits << ")" );
          }

          bits[word_idx] |= (digit << ((digit_idx % g_bit_word_sz)*4));

          digit_idx++;
          if ( (digit_idx*4 % g_bit_word_sz) == 0 )
            word_idx++;

        }
        else if ( str[i] != '_' )
          STDX_THROW( BitContainerExceptions::EInvalidStringConversion,
                      "Could not parse digit " << i << " of " << str );

      }
    }

    // Invalid prefix

    else
      STDX_THROW( BitContainerExceptions::EInvalidStringConversion,
                  "Bit string \"" << str << "\" must have 0b|0x prefix" );

  }

  //----------------------------------------------------------------------
  // bits_left_shift
  //----------------------------------------------------------------------

  void bits_left_shift( BitWord words[], int size, int amt )
  {
    if ( amt != 0 ) {
      int word_lshift = amt / g_bit_word_sz;
      int bit_lshift  = amt % g_bit_word_sz;
      int bit_rshift  = g_bit_word_sz - bit_lshift;

      if ( bit_lshift == 0 ) {
        for ( int idx = size-1; idx >= word_lshift; idx-- )
          words[idx] = words[idx-word_lshift];
      }

      else {

        // We have to decrement the index so we don't overwrite the source

        for ( int idx = size-1; idx >= word_lshift; idx-- ) {
          int src_idx = idx - word_lshift;

          // Set the top bits from the current source word
          words[idx] = words[src_idx] << bit_lshift;

          // Or in the bottom bits from the previous source word
          if ( src_idx-1 >= 0 )
            words[idx] |= words[src_idx-1] >> bit_rshift;
        }

      }

      // Zero bottom words (which were "shifted in")

      for ( int idx = 0; idx < word_lshift; idx++ )
        words[idx] = g_bit_word_0;

    }
  }

  //----------------------------------------------------------------------
  // bits_right_shift
  //----------------------------------------------------------------------

  void bits_right_shift( BitWord words[], int size, int amt )
  {
    if ( amt != 0 ) {
      int word_rshift = amt / g_bit_word_sz;
      int bit_rshift  = amt % g_bit_word_sz;
      int bit_lshift  = g_bit_word_sz - bit_rshift;

      if ( bit_rshift == 0 ) {
        for ( int idx = 0; idx < (size - word_rshift); idx++ )
          words[idx] = words[idx+word_rshift];
      }

      else {
        for ( int idx = 0; idx < (size - word_rshift); idx++ ) {
          int src_idx = idx + word_rshift;

          // Set the bottom bits from the current source word
          words[idx] = words[src_idx] >> bit_rshift;

          // Or in the top bits from the next source word
          if ( (src_idx+1 < size) && (bit_rshift > 0) )
            words[idx] |= words[src_idx+1] << bit_lshift;
        }
      }

      // Zero top words (which were "shifted in")

      for ( int idx = size-word_rshift; idx < size; idx++ )
        words[idx] = g_bit_word_0;

    }
  }

  //----------------------------------------------------------------------
  // bits_right_shifted_copy
  //----------------------------------------------------------------------
  // The number of destination words * bit_word_sz needs to be less than
  // or equal to the number of source words * bit_word_sz - amt. This is
  // what will happen when we use this for extracting a bit field.

  void bits_right_shifted_copy( const BitWord words[], int size,
                                BitWord dest_words[],
                                int dest_size, int amt )
  {
    int num_src_words  = size;
    int num_dest_words = dest_size;
    int word_rshift    = amt / g_bit_word_sz;
    int bit_rshift     = amt % g_bit_word_sz;
    int bit_lshift     = g_bit_word_sz - bit_rshift;

    if ( bit_rshift == 0 ) {
      for ( int idx = 0; idx < num_dest_words; idx++ )
        dest_words[idx] = words[idx+word_rshift];
    }

    else {
      for ( int idx = 0; idx < num_dest_words; idx++ ) {
        int src_idx = idx + word_rshift;

        // Set the bottom bits from the current source word
        dest_words[idx] = words[src_idx] >> bit_rshift;

        // Or in the top bits from the next source word
        if ( (src_idx+1 < num_src_words) && (bit_rshift > 0) )
          dest_words[idx] |= words[src_idx+1] << bit_lshift;

      }
    }
  }

  //----------------------------------------------------------------------
  // bits_reset
  //----------------------------------------------------------------------

  void bits_reset( BitWord words[], int pos, int len )
  {
    int msb      = pos+len-1;
    int lsb      = pos;
    int msb_word = msb / g_bit_word_sz;
    int lsb_word = lsb / g_bit_word_sz;

    // lbits = num of zeros on the least significant side of lsb word
    // mbits = num of zeros on the most significant side of msb word

    int lbits = lsb % g_bit_word_sz;
    int mbits = g_bit_word_sz - (msb % g_bit_word_sz) - 1;

    if ( msb_word != lsb_word ) {
      words[lsb_word] &= ~((~g_bit_word_0 >> lbits) << lbits);

      for ( int idx = lsb_word+1; idx < msb_word; idx++ )
        words[idx] = g_bit_word_0;

      words[msb_word] &= ~((~g_bit_word_0 << mbits) >> mbits);
    }
    else {

      // If the field is completely contained within one word then we
      // need to handle things a bit differently

      words[msb_word]
        &= ~((~g_bit_word_0 >> lbits) << (lbits + mbits) >> mbits);

    }
  }

  //----------------------------------------------------------------------
  // bits_left_shifted_or
  //----------------------------------------------------------------------

  void bits_left_shifted_or( BitWord words[], int size,
                             const BitWord src_words[],
                             int src_size, int amt )
  {
    int num_dest_words = size;
    int num_src_words  = src_size;
    int word_lshift    = amt / g_bit_word_sz;
    int bit_lshift     = amt % g_bit_word_sz;
    int bit_rshift     = g_bit_word_sz - bit_lshift;

    if ( bit_lshift == 0 ) {
      for ( int idx = 0; idx < num_src_words; idx++ )
        words[idx+word_lshift] |= src_words[idx];
    }

    else {

      // Which destination word will hold the top bit of the src words

      int word_top
        = (amt + num_src_words*g_bit_word_sz - 1) / g_bit_word_sz;

      // Or in the first word

      if ( word_top < num_dest_words )
        words[word_top] |= src_words[num_src_words-1] >> bit_rshift;

      // We decrement the index so that the code is similar to the
      // bits_left_shift and (hopefully) easier to get right

      for ( int idx = word_top-1; idx >= 0; idx-- ) {
        int src_idx = idx - word_lshift;

        // Or in the top bits from the current source word
        words[idx] |= src_words[src_idx] << bit_lshift;

        // Or in the bottom bits from the previous source word
        if ( src_idx-1 >= 0 )
          words[idx] |= src_words[src_idx-1] >> bit_rshift;
      }
    }
  }

}}

