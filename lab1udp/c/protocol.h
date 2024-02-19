//
// Created by imat on 26.11.23.
//

#ifndef C_SERVER_PROTOCOL_H
#define C_SERVER_PROTOCOL_H

#include <string.h>
#include <stdlib.h>

struct protocol_header_struct {
    unsigned short content_length;
    unsigned int sequence_number;
};

typedef struct protocol_header_struct protocol_header_t;

#define HEADER_SIZE (sizeof(protocol_header_t))

const char* ERROR_MESSAGE = "ERROR";
const char* OK_MESSAGE = "OK";

//returns packet size
long generate_data_packet(char *packet, protocol_header_t* header) {
    *(protocol_header_t*)packet = *header;
    for (int i = 0; i < header->content_length; i++) {
        *(packet + HEADER_SIZE + i) = 'A' + (i % ('Z' - 'A' + 1));
    }
    return HEADER_SIZE + header->content_length;
}

//returns packet size
long generate_response_packet(char *packet, protocol_header_t* header, int check)
{
    *(protocol_header_t*)packet = *header;
    switch (check) {
        case 0:
            strcpy(packet+HEADER_SIZE, ERROR_MESSAGE);
            return HEADER_SIZE + sizeof ERROR_MESSAGE - 1;
            break;
        case 1:
            strcpy(packet+HEADER_SIZE, OK_MESSAGE);
            return HEADER_SIZE + sizeof OK_MESSAGE - 1;
            break;
        default:
            perror("Invalid check value");
            exit(1);
    }
}

// returns 1 if correct, 0 if error
int check_packet(const char *packet) {
    protocol_header_t* header = (protocol_header_t *)packet;
    packet += HEADER_SIZE;
    for (int i = 0; i < header->content_length; ++i) {
        if (*(packet + i) != 'A' + (i % ('Z' - 'A' + 1))) return 0;
    }
    return 1;
}

#endif //C_SERVER_PROTOCOL_H
