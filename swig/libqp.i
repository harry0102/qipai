/* file : libqp.i */
%module libqp
%{
#include "../src/ht_str.h"
#include "../src/card.h"
#include "../src/hand.h"
#include "../src/deck.h"
#include "../src/sort_card.h"
#include "../src/card_player.h"
#include "../src/ddz.h"
#include "../src/gp.h"
#include "../src/texas.h"
%}

%include "../src/ht_str.h"
%include "../src/card.h"
%include "../src/hand.h"
%include "../src/deck.h"
%include "../src/sort_card.h"
%include "../src/card_player.h"
%include "../src/ddz.h"
%include "../src/gp.h"
%include "../src/texas.h"

/* helper function */
%inline %{
/* ddz */
card_player_t* ddz_get_player(ddz_t* ddz, int player_no){
    if(ddz && player_no >= 0 && player_no < 3)
        return &(ddz->players[player_no]);
    else
        return 0;
}
hand_t* ddz_get_player_hand(card_player_t* player){
    if(player)
        return player->mycards;
    else
        return 0;
}
card_t* ddz_get_di(ddz_t* ddz, int index){
    if(ddz && index >= 0 && index < 3)
        return &(ddz->di[index]);
    else
        return 0;
}
int ddz_landlord_call(ddz_t* ddz){
    if(ddz)
        return ddz->call[ddz->landlord_no];
    else
        return 0;
}
/* gp */
card_player_t* gp_get_player(gp_t* gp, int player_no){
    if(gp && player_no >= 0 && player_no < gp->player_num)
        return &(gp->players[player_no]);
    else
        return 0;
}
hand_t* gp_get_player_hand(card_player_t* player){
    if(player)
        return player->mycards;
    else
        return 0;
}
/* texas */
card_player_t* texas_get_player(texas_t* texas, int player_no){
    if(texas && player_no >= 0 && player_no < texas->player_num)
        return &(texas->players[player_no]);
    else
        return 0;
}
hand_t* texas_get_player_hand(card_player_t* player){
    if(player)
        return player->mycards;
    else
        return 0;
}
card_t* texas_get_board(texas_t* texas, int index){
    if(texas && index >= 0 && index < 5)
        return &(texas->board[index]);
    else
        return 0;
}
%}


