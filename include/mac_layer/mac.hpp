/*!
 * @file mac.h
 * @author Steven Knudsen
 * @date May 25, 2021
 *
 * @details The MAC class. It handles CSP packets received from the application
 * layer, processes them to make transparent more packets, and sends them to
 * the PHY. It also receives transparent mode packets, processes them, and
 * reassembles them into CSP packets to be sent to the application layer.
 *
 * @copyright University of Alberta, 2021
 *
 * @license
 * This software may not be modified or distributed in any form, except as described in the LICENSE file.
 */

#ifndef EX2_SDR_MAC_LAYER_MAC_H_
#define EX2_SDR_MAC_LAYER_MAC_H_

#include <mutex>
#include <stdexcept>
#include <queue>
#include <vector>
#include <time.h>

#ifdef __cplusplus
extern "C" {
#endif

#include "csp_types.h"

#ifdef __cplusplus
}
#endif

#include "FEC.hpp"
#include "ppdu_cf.hpp"
#include "ppdu_u8.hpp"
#include "mpdu.hpp"
#include "rfMode.hpp"

// TODO This definition belongs somewhere else
#define CSP_MTU_LENGTH ( 4096 )

#define MAC_MAX_RX_BUFFERS MAC_SERVICE_QUEUE_LENGTH
#define MAC_MAX_TX_BUFFERS MAC_SERVICE_QUEUE_LENGTH


namespace ex2
{
  namespace sdr
  {

    /*!
     * @brief This is the media access controller (MAC)
     *
     * @details The MAC class is a singleton that instantiates two tasks that
     * manage queues to the CSP server. One queue transports CSP packets from
     * the CSP server to the MAC that are to be transmitted by the UHF radio.
     * The other queue is used by the MAC to send CSP packets up to the CSP
     * server that are reconstructed from packets received by the UHF Radio.
     *
     *
     * @todo Add diagrams (state machine, messaging, other)?
     */
    class MAC
    {
    public:

      /*!
       * @brief Constructor
       *
       * @param rfModeNumber The UHF radio modulation in use.
       * @param errorCorrectionScheme The FEC scheme in use.
       */
      MAC (RF_Mode::RF_ModeNumber rfModeNumber,
        ErrorCorrection::ErrorCorrectionScheme errorCorrectionScheme);

      ~MAC ();

      // @todo is this best or should I make it a plain enum so that the wrapper
      // is more transparent? That is, would it be less to maintain?
      enum class MAC_UHFPacketProcessingStatus : uint16_t {
        // All the necessary UHF packets have been received and a CSP packet
        // was formed and must be removed.
        CSP_PACKET_READY = 0x0000,
        // Not all the necessary UHF packets have been received, but there are
        // no more expected. A CSP packet was formed and must be removed. Then
        // the last UHF packet must be resubmitted.
        CSP_PACKET_READY_RESUBMIT_PREVIOUS_PACKET = 0x0001,
        // Not all the necessary UHF packets have been received, waiting for
        // the next one.
        READY_FOR_NEXT_UHF_PACKET = 0x0002
        // @todo is another value needed to indicate that the first packet of
        // a CSP packet was not received? Or is READY_FOR_NEXT_UHF_PACKET good
        // enough
      };

      /*!
       * @brief Process the received UHF data as an MPDU.
       *
       * @details Process each MPDU received (UHF received data in transparent
       * mode) until a full CSP packet is received or there is an error.
       *
       * @param uhfPayload
       * @param payloadLength
       *
       * @return The status of the process operation.
       */
      MAC_UHFPacketProcessingStatus processUHFPacket(const uint8_t *uhfPayload, const uint32_t payloadLength);

      /*!
       * @brief Return the number of MPDUs needed to transmit the received
       * CSP packet
       *
       * @details This is useful for unit testing.
       *
       * @todo Perhaps make this protected and the unit test a friend class?
       *
       * @param cspPacket
       * @return
       */
      uint32_t numMPDUsInCSPPacket(csp_packet_t * cspPacket);

      /*!
       * @brief Receive and encode new CSP packet.
       *
       * @details Processed the received CSP packet to create MPDUs ready for
       * transmission by the UHF radio in transparent mode. This function
       * should be followed by repeated calls to @p nextMPDU until all MPDUs
       * corresponding to the current CSP have been created and transimitted.
       *
       * @note This is valid as of the most recent CSP packet processed by
       * @p receiveCSPPacket()
       *
       * @param cspPacket
       *
       * @return True if the CSP packet was encoded, false otherwise
       */
      bool receiveCSPPacket(csp_packet_t * cspPacket);

      /*!
       * @brief The length of each MPDU payload in the MPDU Payload buffer in bytes.
       *
       * @details The nominal length for a transparent mode payload is 128 bytes.
       * However, this code may be used for radios other than the EnduroSat
       * UHF Type II, so it's best to have the ability to check.
       *
       * @note This is valid as of the most recent CSP packet processed by
       * @p receiveCSPPacket()
       *
       * @return Length of each MPDU payload in the MPDU Payload buffer in bytes.
       */
      uint32_t mpduPayloadLength() const;

      /*!
       * @brief Pointer to MPDU payloads buffer.
       *
       * @details This is needed for the C wrapper accessor
       *
       * @return pointer to the MPDU payloads buffer.
       */
      uint8_t * mpduPayloadsBuffer();

      /*!
       * @breif The number of bytes in the MPDU payloads buffer.
       *
       * @return Number of bytes in the MPDU payloads buffer.
       */
      uint32_t mpduPayloadsBufferLength() const;

      /*!
       * @brief An iterator that provides MPDUs corresponding to a CSP packet.
       *
       * @todo need this?
       *
       * @details Each invocation of this function returns the next MPDU
       * corresponding to a CSP packet that was passed to @p newCSPPacket.
       *
       * @param[in out] mpdu The MPDU contents are replaced by the next MPDU
       * corresponding to the received CSP packet, or zeroed if there are no more.
       *
       * @return true if there is at least one more MPDU, in which case the @p
       * mpdu contains a valid MPDU that should be transmitted. false if there
       * are no more MPDUs.
       */
//      bool nextMPDU(MPDU &mpdu);

      /*!
        * @brief A kind of iterator that provides MPDUs corresponding to a CSP packet.
        *
        * @todo need this?
        *
        * @details Each invocation of this function returns the next MPDU
        * corresponding to a CSP packet that was passed to @p newCSPPacket.
        *
        * @param[in out] mpdu The MPDU contents are replaced by the next MPDU
        * corresponding to the received CSP packet, or zeroed if there are no more.
        *
        * @return true if there is at least one more MPDU, in which case the @p
        * mpdu contains a valid MPDU that should be transmitted. false if there
        * are no more MPDUs.
        */
//       bool nextTransparentModePayload();

      /*!
       * @brief Accessor
       *
       * @return The ErrorCorrectionScheme in use
       */
      ErrorCorrection::ErrorCorrectionScheme
      getErrorCorrectionScheme () const
      {
        return m_errorCorrection->getErrorCorrectionScheme();
      }

      /*!
       * @brief Accessor
       *
       * @param ecScheme The ErrorCorrectionScheme to use
       */
      void setErrorCorrectionScheme (
        ErrorCorrection::ErrorCorrectionScheme errorCorrectionScheme);

      /*!
       * @brief Accessor
       *
       * @return The UHF Radio RF Mode in use
       */
      RF_Mode::RF_ModeNumber
      getRFModeNumber () const
      {
        return m_rfModeNumber;
      }

      /*!
       * @brief Accessor
       *
       * @param rfModeNumber The UHF Radio RF Mode to use
       */
      void
      setRFModeNumber (
        RF_Mode::RF_ModeNumber rfModeNumber)
      {
        m_rfModeNumber = rfModeNumber;
      }

      const std::vector<uint8_t>&
      getRawCspPacket () const
      {
        return m_rawCSPPacket;
      }

    private:

      void m_updateErrorCorrection(
        ErrorCorrection::ErrorCorrectionScheme errorCorrectionScheme);

      void m_decodeCSPPacket();

      // member vars that define the MAC operation
      ErrorCorrection *m_errorCorrection = 0;

      FEC *m_FEC;

      RF_Mode::RF_ModeNumber m_rfModeNumber;

      uint32_t m_numMPDUsPerCodeword;

      // member vars that define the structure of a fragmented CSP packet
      uint16_t m_numCodewordFragments;
      uint16_t m_messageLength;

      // Mutexs to ensure that in progress packet processing is not corrupted
      // by an inadvertant change in FEC parameters
//      std::mutex m_ecSchemeMutex;

      // buffers needed to fragment a CSP Packet prior to transmission
      std::vector<uint8_t> m_codewordBuffer;
      std::vector<uint8_t> m_transparentModePayloads;
//      void m_clearFIFO(std::queue<PPDU_u8::payload_t> &fifo);

      // buffers needed to handle received CSP packet fragments
      std::vector<uint8_t> m_receiveCSPBuffer;

      // member vars to track received CSP packet fragments
      bool m_firstCSPFragmentReceived;
      uint16_t m_currentCSPPacketLength;
      uint16_t m_expectedMPDUs;
      uint16_t m_mpduCount;
      uint16_t m_userPacketFragementCount;

      float m_SNREstimate;

      std::vector<uint8_t> m_rawCSPPacket;
    };

  } // namespace sdr
} // namespace ex2

#endif /* EX2_SDR_MAC_LAYER_MAC_H_ */

