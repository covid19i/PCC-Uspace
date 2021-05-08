#include <unistd.h>
#include <cstdlib>
#include <cstring>
#include <netdb.h>
#include <iostream>
#include <fstream>
#include "../core/udt.h"
#include "../core/options.h"

using namespace std;

void* senddata(void*);
void* recvdata(void*);
void* recv_monitor(void* s);
void* send_monitor(void* s);

void prusage() {
    cout << "usage: appserver <send|recv> [server_port]" << endl;
    exit(-1);
}

int main(int argc, char* argv[]) {

    if (strcmp(argv[1], "recv") && strcmp(argv[1], "send"))   {
        prusage();
    }
    Options::Parse(argc, argv);

    bool should_recv = !strcmp(argv[1], "recv");

    UDT::startup();

    addrinfo hints;
    addrinfo* res;

    memset(&hints, 0, sizeof(struct addrinfo));

    hints.ai_flags = AI_PASSIVE;
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    string service(argv[2]);

    if (0 != getaddrinfo(NULL, service.c_str(), &hints, &res)) {
        cout << "illegal port number or port is busy.\n" << endl;
        return 0;
    }

    UDTSOCKET serv = UDT::socket(res->ai_family, res->ai_socktype, res->ai_protocol);

    if (UDT::ERROR == UDT::bind(serv, res->ai_addr, res->ai_addrlen)) {
        cout << "bind: " << UDT::getlasterror().getErrorMessage() << endl;
        return 0;
    }

    freeaddrinfo(res);

    cout << "server is ready at port: " << service << endl;

    if (UDT::ERROR == UDT::listen(serv, 10)) {
        cout << "listen: " << UDT::getlasterror().getErrorMessage() << endl;
        return 0;
    }

    sockaddr_storage clientaddr;
    int addrlen = sizeof(clientaddr);

    UDTSOCKET udt_socket;

    while (true) {
        if (UDT::INVALID_SOCK == (udt_socket = UDT::accept(serv, (sockaddr*)&clientaddr, &addrlen))) {
            cout << "accept: " << UDT::getlasterror().getErrorMessage() << endl;
            return 0;
        }

        char clienthost[NI_MAXHOST];
        char clientservice[NI_MAXSERV];
        getnameinfo((sockaddr *)&clientaddr, addrlen, clienthost, sizeof(clienthost), clientservice, sizeof(clientservice), NI_NUMERICHOST|NI_NUMERICSERV);
        cout << "new connection: " << clienthost << ":" << clientservice << endl;

        pthread_t worker_thread;
        if (should_recv) {
            pthread_create(&worker_thread, NULL, recvdata, new UDTSOCKET(udt_socket));
        } else {
            pthread_create(&worker_thread, NULL, senddata, new UDTSOCKET(udt_socket));
        }
        pthread_detach(worker_thread);
   }

    UDT::close(serv);
    UDT::cleanup();

    return 0;
}

void* senddata(void* usocket)
{
   UDTSOCKET sender = *(UDTSOCKET*)usocket;
   delete (UDTSOCKET*)usocket;
   pthread_create(new pthread_t, NULL, send_monitor, &sender);
   char* data;
   int size = 100000000;
   data = new char[size];

   while (true)
   {
      int ssize = 0;
      int ss;
      while (ssize < size)
      {
         if (UDT::ERROR == (ss = UDT::send(sender, data + ssize, size - ssize, 0)))
         {
            cout << "send:" << UDT::getlasterror().getErrorMessage() << endl;
            break;
         }
         ssize += ss;
      }

      if (ssize < size)
         break;
   }

   delete [] data;

   UDT::close(sender);

      return NULL;
}

void* recvdata(void* usocket)
{
   UDTSOCKET recver = *(UDTSOCKET*)usocket;
   delete (UDTSOCKET*)usocket;
   pthread_create(new pthread_t, NULL, recv_monitor, &recver);
   char* data;
   int size = 100000000;
   data = new char[size];

   while (true)
   {
      int rsize = 0;
      int rs;
      while (rsize < size)
      {
         if (UDT::ERROR == (rs = UDT::recv(recver, data + rsize, size - rsize, 0)))
         {
            cout << "recv:" << UDT::getlasterror().getErrorMessage() << endl;
            break;
         }

         rsize += rs;
      }

      if (rsize < size)
         break;
   }

   delete [] data;

   UDT::close(recver);

      return NULL;
}

void* recv_monitor(void* s)
{
   UDTSOCKET u = *(UDTSOCKET*)s;
    int i = 0;

   UDT::TRACEINFO perf;

   fstream rec_output_file;
   rec_output_file.open("/home/lee/Desktop/receiver_output.txt");
   rec_output_file << "Step,Package Sending Peroid,Congestion Window Size,On-Flight Packeage,Bandwidth,Receiving Rate (Mbps),Sending Time (ms),RTT (ms),Sent Total,Received Lost Total,Sending Data Time" << endl;

   cout << "Step\tFlow Window Size\tCongestion Window Size\tBandwidth(Mb/s)\tReceive Rate(Mb/s)\tRTT(ms)\tPackets Received\tTotal Packets Received\tPackets Loss\tTotal Packets Lost" << endl;

   while (true)
   {
      ++i;
         sleep(1);

      if (UDT::ERROR == UDT::perfmon(u, &perf))
      {
         cout << "perfmon: " << UDT::getlasterror().getErrorMessage() << endl;
         break;
      }

      cout   << i <<"\t"
         << perf.pktFlowWindow    << "\t\t"         // flow window size, in number of packets
         << perf.pktCongestionWindow    << "\t\t"   // congestion window size, in number of packets
         << perf.mbpsBandwidth    << "\t\t"         // estimated bandwidth, in Mb/s
         << perf.mbpsRecvRate    << "\t\t"          // receive rate in Mb/s
         << perf.msRTT           << "\t\t"          // RTT, in milliseconds
         << perf.pktRecv    << "\t\t"               // number of received packets
         << perf.pktRecvTotal    << "\t\t"          // total number of received packets
         << perf.pktRcvLoss    << "\t\t"            // number of lost packets (receiver side)
         << perf.pktRcvLossTotal    << endl;        // number of lost packets (receiver side)

      if(i < 101){
            rec_output_file << i << ","
            << perf.pktFlowWindow    << ","
            << perf.pktCongestionWindow    << ","
            << perf.mbpsBandwidth    << ","
            << perf.mbpsRecvRate    << ","
            << perf.msRTT           << ","
            << perf.pktRecv    << ","
            << perf.pktRecvTotal    << ","
            << perf.pktRcvLoss    << ","
            << perf.pktRcvLossTotal    << endl;
        } else {
            if(rec_output_file.is_open()){
                rec_output_file.close();
            }
        }
   }

      return NULL;
}

void* send_monitor(void* s)
{
   UDTSOCKET u = *(UDTSOCKET*)s;
    int i = 0;

   UDT::TRACEINFO perf;

   fstream snd_output_file;
   snd_output_file.open("/home/lee/Desktop/sender_output.txt");
   snd_output_file << "Step,Sending Peroid,Busy Sending Time,Flow Window Size,Congestion Window Size,On Flight Packets,Bandwidth,Sending Rate,RTT,Packets Sent,Total Packets Sent,Send Duration,Total Send Duration,Packets Lost,Total Packets Lost" << endl;

   cout << "Step\tSending Peroid(ms)\tBusy Sending Time\tFlow Window Size\tCongestion Window Size\tOn Flight Packets\tBandwidth(Mb/s)\tSending Rate(Mb/s)\tRTT(ms)\tPackets Sent\tTotal Packets Sent\tSend Duration\tTotal Send Duration\tPackets Lost\tTotal Packets Lost" << endl;

   while (true)
   {
      ++i;
         sleep(1);

      if (UDT::ERROR == UDT::perfmon(u, &perf))
      {
         cout << "perfmon: " << UDT::getlasterror().getErrorMessage() << endl;
         break;
      }

      cout   << i <<"\t"
         << perf.usPktSndPeriod    << "\t\t"        // packet sending period, in microseconds
         << perf.mbpsGoodput    << "\t\t"           // busy sending time (i.e., idle time exclusive)
         << perf.pktFlowWindow    << "\t\t"         // flow window size, in number of packets
         << perf.pktCongestionWindow    << "\t\t"   // congestion window size, in number of packets
         << perf.pktFlightSize    << "\t\t"         // number of packets on flight
         << perf.mbpsBandwidth    << "\t\t"         // estimated bandwidth, in Mb/s
         << perf.mbpsSendRate    << "\t\t"          // sending rate in Mb/s
         << perf.msRTT           << "\t\t"          // RTT, in milliseconds
         << perf.pktSent    << "\t\t"               // number of sent data packets, including retransmissions
         << perf.pktSentTotal    << "\t\t"          // total number of sent data packets, including retransmissions
         << perf.usSndDuration    << "\t\t"         // busy sending time (i.e., idle time exclusive)
         << perf.usSndDurationTotal    << "\t\t"    // total time duration when UDT is sending data (idle time exclusive)
         << perf.pktSndLoss    << "\t\t"           // number of lost packets (sender side)
         << perf.pktSndLossTotal << endl;           // total number of lost packets (sender side)

      if(i < 101){
            snd_output_file << i <<","
            << perf.usPktSndPeriod    << ","        
            << perf.mbpsGoodput    << ","       
            << perf.pktFlowWindow    << ","         
            << perf.pktCongestionWindow    << ","   
            << perf.pktFlightSize    << ","         
            << perf.mbpsBandwidth    << ","         
            << perf.mbpsSendRate    << ","          
            << perf.msRTT           << ","          
            << perf.pktSent    << ","          
            << perf.pktSentTotal    << ","          
            << perf.usSndDuration    << ","    
            << perf.usSndDurationTotal    << ","    
            << perf.pktSndLoss    << ","    
            << perf.pktSndLossTotal << endl;   
        } else {
            if(snd_output_file.is_open()){
                snd_output_file.close();
            }
        }

   }

      return NULL;
}
