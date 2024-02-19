#define MAX_TEXT_LEN 255
#define STATIC_NODE_PART_LEN 276

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <math.h>
#include <stdbool.h>


struct serialized_node{
    int id;
    int next_id;
    short rating;
    unsigned int price;
    char title[MAX_TEXT_LEN];
    unsigned int content_length;
};
typedef struct serialized_node snode_t;

struct node {
    struct node *next;
    int id;
    int next_id;
    short rating;
    unsigned int price;
    char title[MAX_TEXT_LEN];
    unsigned int content_length;
    char* content;
};
typedef struct node node_t;

void print_node(node_t *n) {
    printf("Node: %i, rating: %i, price: %i, title: \"%s\", content length: %u, content: \"%s\"",
           n->id, n->rating, n->price, n->title, n->content_length, n->content);
}

struct linked_list {
    node_t *head;
    node_t *tail;
    int n_nodes;
    unsigned int total_content_length;
};
typedef struct linked_list linked_list_t;

void fill_node(node_t *node, int id, short rating, unsigned int price,
               char *title, unsigned int content_length, char *content) {
    node->id = id;
    node->rating = rating;
    node->price = price;
    strcpy(node->title, title);
    node->content_length = content_length;
    node->content = content;
}

void copy_fields_to_sn(node_t *node, snode_t *snode){
    snode->content_length = node->content_length;
    snode->next_id = node->next_id;
    snode->id = node->id;
    snode->rating = node->rating;
    snode->price = node->price;
    strcpy(snode->title, node->title);
}

void serialize_node(char *buffer, node_t *node){
    struct serialized_node sn;
    copy_fields_to_sn(node, &sn);
    memcpy(buffer, &sn, sizeof (sn));
    memcpy(buffer+STATIC_NODE_PART_LEN, node->content, node->content_length);
}

char* serialize_list(linked_list_t *ll, unsigned int* buf_len){
    unsigned int len = ll->n_nodes * STATIC_NODE_PART_LEN + ll->total_content_length + 4;
    char *buffer = malloc(len);
    memcpy(buffer, &ll->n_nodes, 4);
    node_t *t = ll->head;
    unsigned int write_from = 4;
    while (t){
        serialize_node(buffer + write_from, t);
        write_from += STATIC_NODE_PART_LEN + t->content_length;
        t = t->next;
    }
    *buf_len = len;
    return buffer;
}

void copy_fields_from_sn(node_t *node, snode_t *snode){
    node->content_length = snode->content_length;
    node->next_id = snode->next_id;
    node->id = snode->id;
    node->rating = snode->rating;
    node->price = snode->price;
    strcpy(node->title, snode->title);
}

void deserialize_node(char *buffer, node_t *node){
    snode_t sn;
    memcpy(&sn, buffer, STATIC_NODE_PART_LEN);
    char *str = malloc(sn.content_length);
    node->content = str;
    memcpy(str, buffer+STATIC_NODE_PART_LEN, sn.content_length);
    copy_fields_from_sn(node, &sn);
}

void deserialize_list(char *buffer, int buffer_size, linked_list_t *ll){
    unsigned int read_from = 4;
    int n_nodes = *(int*)(buffer);
    node_t *nodes[n_nodes];
    bool is_head[n_nodes];
    for (int i = 0; i < n_nodes; i++){
        is_head[i] = true;
    }
    // read all nodes
    ll->n_nodes = 0;
    for (int i = 0; i < n_nodes && read_from + STATIC_NODE_PART_LEN < buffer_size; i++) {
        node_t *t = malloc(sizeof(node_t));
        deserialize_node(buffer + read_from, t);
        read_from += STATIC_NODE_PART_LEN + t->content_length;
        nodes[i] = t;
        ll->total_content_length += t->content_length;
        ll->n_nodes += 1;
        if (t->next_id == -1){
            ll->tail = t;
        }
    }
    // connect nodes with their next nodes
    for (int i = 0; i < ll->n_nodes; i++){
        node_t *t = nodes[i];
        for (int j = i+1; j < ll->n_nodes; j++){
            node_t *n = nodes[j];
            if (t->next_id == n->id){
                t->next = n;
                is_head[j] = false;
            }
            if (t->id == n->next_id){
                n->next = t;
                is_head[i] = false;
            }
        }
    }
    for (int i = 0; i < n_nodes; i++){
        if (is_head[i]){
            ll->head = nodes[i];
        }
    }
    // if no tail found set the tail to be the last reachable node from the head
    if (!ll->tail){
        printf("No end of list found :(\n");
        node_t *t = ll->head;
        while (t->next){
            t = t->next;
        }
        ll->tail = t;
        t->next_id = -1;
    }
}

void free_list(node_t *head) {
    node_t *next;
    while (head) {
        next = head->next;
        free(head->content);
        free(head);
        head = next;
    }
}

void add_node_to_list(linked_list_t *ll, node_t *node) {
    ll->n_nodes += 1;
    ll->total_content_length += node->content_length;
    if (!ll->head) {
        ll->head = node;
    } else {
        ll->tail->next = node;
        ll->tail->next_id = node->id;
    }
    ll->tail = node;
    ll->tail->next_id = -1;
    ll->tail->next = (node_t *) 0;
}

void print_linked_list(linked_list_t *ll) {
    node_t *t = ll->head;
    while (t) {
        print_node(t);
        printf("\n");
        t = t->next;
    }
}


linked_list_t* prepare_data(int n_nodes){
    linked_list_t *ll = malloc(sizeof(linked_list_t));
    node_t *t;
    for (int i = 0; i < n_nodes; i++){
        t = malloc(sizeof(node_t));
        char title[100];
        char *content = malloc(65536);

        sprintf(title, "Book by %i", i);
        strcpy(content, "A long ");
        int j = 0;
        for (; j < i; j++){
            strcpy(content + 7+j*5, "long ");
        }
        strcpy(content+7+j*5, "time ago...");

        fill_node(t, i, (short) i*2, i*3,  title, 7+j*5+11, content);
        add_node_to_list(ll, t);
    }
    return ll;
}

