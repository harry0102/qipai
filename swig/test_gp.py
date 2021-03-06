#!/usr/bin/env python
import wx
import libqp

USE_BUFFERED_DC = True

class GameFrame(wx.Frame):
    """ Draw a line to a pannel."""
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(820,580))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        
        # control
        self.btn_start = wx.Button(self, id=-1, label='NewGame',
            pos=(0,0), size=(100,28))
        self.btn_start.Bind(wx.EVT_BUTTON, self.ButtonStart)
        self.btn_start.SetToolTip(wx.ToolTip("start a new game"))
        self.btn_estimate = wx.Button(self, id=-1, label='Estimate',
            pos=(0,0), size=(100,28))
        self.btn_estimate.Bind(wx.EVT_BUTTON, self.ButtonEstimate)
        self.btn_estimate.SetToolTip(wx.ToolTip("estimate a hand type")) 
        self.cb_rule = wx.CheckBox(self, id=-1, label='Zhuji rule',
            pos=(0,0), size=(100, 20))
        self.cb_rule.Bind(wx.EVT_CHECKBOX, self.CBRuleClick)
        
        # load all cards image
        suit = ['S','H','C','D']
        rank = ['A','2','3','4','5','6','7','8','9','T','J','Q','K']
        self.bmpPoker = {}
        bmp = wx.EmptyBitmap(1, 1)
        bmp.LoadFile("../data/poker/0.png", wx.BITMAP_TYPE_ANY)
        self.bmpPoker['0'] = bmp
        for s in suit:
            for r in rank:
                keyname = "%s%s" % (s, r)
                bmpname = "../data/poker/%s.png" % keyname
                bmp = wx.EmptyBitmap(1, 1)
                bmp.LoadFile(bmpname, wx.BITMAP_TYPE_ANY)
                self.bmpPoker[keyname] = bmp
        bmp = wx.EmptyBitmap(1, 1)
        bmp.LoadFile("../data/poker/JS.png", wx.BITMAP_TYPE_ANY)
        self.bmpPoker['*S'] = bmp
        bmp = wx.EmptyBitmap(1, 1)
        bmp.LoadFile("../data/poker/JB.png", wx.BITMAP_TYPE_ANY)
        self.bmpPoker['*B'] = bmp
        
        self.infoW = 58
        self.blankH = 30
        self.upH = 19
        self.pokerOffsetW = 21
        self.rcHand = []
        self.rcHand.append(wx.Rect(self.infoW, 0, 0, 0))
        self.rcHand.append(wx.Rect(self.infoW, 0, 0, 0))
        self.flag_up = [0] * 50
        
        # create game logic
        self.sel_handtype = 0
        self.sel_handparam = 0    
        self.gp = libqp.gp_new(0)
        self.gp.player_num = 2
        self.NewGame()

    def NewGame(self):
        libqp.gp_start(self.gp)

        # sort
        for i in range(0, 3):
            player = libqp.gp_get_player(self.gp, i)
            hand = libqp.gp_get_player_hand(player)
            libqp.cards_sort(hand)
        # recalc all rect
        self.CalcRect()
        self.Refresh()        
    
    def ButtonStart(self, e):
        self.NewGame()

    def ButtonEstimate(self, e):
        cp_no = self.gp.curr_player_no
        outlist = []
        for i in range(0, 50):
            if self.flag_up[i] > 0:
                outlist.append(i)
        if len(outlist) > 0:
            player = libqp.gp_get_player(self.gp, cp_no)
            hand_p = libqp.gp_get_player_hand(player)
            hand_out = libqp.hand_new(len(outlist))
            for j in outlist:
                card = libqp.hand_get(hand_p, j)
                libqp.hand_push(hand_out, card)
            libqp.gp_handtype(self.gp, hand_out)
            self.sel_handtype = hand_out.type
            self.sel_handparam = hand_out.param
            self.Refresh()


    def CBRuleClick(self, e):
        if(self.gp.game_rule == 0):
            rule = 1
        else:
            rule = 0
        self.gp = libqp.gp_new(rule)
        self.gp.player_num = 2
        self.NewGame()
                
    def OnPaint(self, e):
        width, height = self.GetClientSize()
        
        if USE_BUFFERED_DC:
            dc = wx.BufferedPaintDC(self, self._Buffer)
        else:
            dc = wx.PaintDC(self)
        brBack = wx.Brush('#053154', wx.SOLID);
        dc.SetBackground(brBack)
        dc.Clear()
        
        pokerW, pokerH = self.bmpPoker['0'].GetSize()
        x = 0
        y = 0
           
        # draw player's hand cards
        dc.SetTextForeground(wx.WHITE)
        for i in range(0, 2):
            x = 0
            cp_no = self.gp.curr_player_no
            playerid = "player%d" % (1 - i)
            dc.DrawText(playerid, x, self.rcHand[1-i].GetY())
            if cp_no == (1 - i):
                # draw arrow
                arlist = [(0,0), (8,8), (0,16)]
                dc.DrawPolygon(arlist, self.rcHand[1-i].GetX() - 10,
                    self.rcHand[1-i].GetY() + pokerH / 2 - 8)

            player = libqp.gp_get_player(self.gp, 1 - i)
            hand = libqp.gp_get_player_hand(player)
            num = libqp.hand_num(hand)
            x = self.rcHand[1-i].GetX()
            y = self.rcHand[1-i].GetY()
            for j in range(0, num):
                card = libqp.hand_get(hand, j)
                keyname = libqp.card_text(card)
                if self.flag_up[j] > 0 and cp_no == (1 - i):
                    dc.DrawBitmap(self.bmpPoker[keyname], x, y - self.upH, 0)
                else:
                    dc.DrawBitmap(self.bmpPoker[keyname], x, y, 0)
                x = x + self.pokerOffsetW
               
        # draw last hand
        num = self.gp.last_hand.num
        x = (width - ((num - 1) * self.pokerOffsetW + pokerW)) / 2
        for i in range(0, num):
            card = libqp.hand_get(self.gp.last_hand, i)
            keyname = libqp.card_text(card)
            dc.DrawBitmap(self.bmpPoker[keyname], x, 0, 0)
            x = x + self.pokerOffsetW
        
        # info
        info = "rule:%d\n" % self.gp.game_rule
        info += "state:%d\n" % (self.gp.game_state)
        info += "curr player:%d\n" % (self.gp.curr_player_no)
        info += "last hand:%d,%d\n" % (self.gp.last_hand.type,self.gp.last_hand.param)
        info += "select:%d,%d" % (self.sel_handtype,self.sel_handparam)
        dc.DrawText(info, 0, 0)
        #dc.SetPen(wx.Pen('#007F0F', 4))
        #dc.DrawLine(0, 0, 50, 50)
    
    def OnEraseBackground(self, e):
        # Do nothing, to avoid flashing on MSW
        pass

    def OnLeftDown(self, e):
        pokerW, pokerH = self.bmpPoker['0'].GetSize()
        pt = e.GetPosition()
        cp_no = self.gp.curr_player_no
        rc = wx.Rect(self.rcHand[cp_no].GetX(),
            self.rcHand[cp_no].GetY(),
            self.rcHand[cp_no].GetWidth(),
            self.rcHand[cp_no].GetHeight())
        rc.SetY(rc.GetY() - self.upH)
        rc.SetHeight(rc.GetHeight() + self.upH)
        flag = 0
        if rc.Inside(pt):
            player = libqp.gp_get_player(self.gp, cp_no)
            hand = libqp.gp_get_player_hand(player)
            num = libqp.hand_num(hand)
            if pt.x > (rc.GetRight() - pokerW):
                if self.flag_up[num-1] > 0:
                    y1 = rc.GetTop()
                    y2 = y1 + pokerH
                    if pt.y >= y1 and pt.y <= y2:
                        self.flag_up[num-1] = 0
                        flag = 1
                else:
                    y1 = rc.GetTop() + self.upH
                    y2 = y1 + pokerH                    
                    if pt.y >= y1 and pt.y <= y2:
                        self.flag_up[num-1] = 1
                        flag = 1
            else:
                idx = (pt.x - rc.GetLeft()) / self.pokerOffsetW
                if self.flag_up[idx] > 0:
                    y1 = rc.GetTop()
                    y2 = y1 + pokerH
                    if pt.y >= y1 and pt.y <= y2:
                        self.flag_up[idx] = 0
                        flag = 1
                else:
                    y1 = rc.GetTop() + self.upH
                    y2 = y1 + pokerH
                    if pt.y >= y1 and pt.y <= y2:
                        self.flag_up[idx] = 1
                        flag = 1
        if flag > 0:
            self.Refresh()

    # reponse mouse right button
    def OnRightDown(self, e):
        pt = e.GetPosition()
        cp_no = self.gp.curr_player_no
        if self.rcHand[cp_no].Inside(pt):
            outlist = []
            for i in range(0, 50):
                if self.flag_up[i] > 0:
                    outlist.append(i)
            if len(outlist) > 0:
                player = libqp.gp_get_player(self.gp, cp_no)
                hand_p = libqp.gp_get_player_hand(player)
                hand_out = libqp.hand_new(len(outlist))
                for j in outlist:
                    card = libqp.hand_get(hand_p, j)
                    libqp.hand_push(hand_out, card)
                htype = libqp.hand_type()
                libqp.gp_handtype(self.gp, hand_out, htype)
                ret = libqp.gp_canplay(self.gp, hand_out, htype)
                if ret > 0:
                    libqp.gp_play(self.gp, cp_no, hand_out)
                    num = libqp.hand_num(hand_p)
                    pokerW, pokerH = self.bmpPoker['0'].GetSize()
                    self.rcHand[cp_no].SetWidth(pokerW + (num - 1) * self.pokerOffsetW)
                    for i in range(0, 50):
                        self.flag_up[i] = 0
                    self.Refresh()
                else:
                    print "can't play:",htype.type,htype.logic_value1
            else:
                # pass
                libqp.gp_pass(self.gp, cp_no)
                self.Refresh()
        else:
            # reset flag_up
            flag = 0
            for i in range(0, 50):
                if self.flag_up[i] > 0:
                    flag = 1
                    self.flag_up[i] = 0
            if flag > 0:
                self.Refresh()
    
    def CalcRect(self):
        width, height = self.GetClientSize()
        pokerW, pokerH = self.bmpPoker['0'].GetSize()
        y = height
        for i in range(0, 2):
            self.rcHand[1-i].SetY(y - pokerH)
            player = libqp.gp_get_player(self.gp, 1 - i)
            hand = libqp.gp_get_player_hand(player)
            num = libqp.hand_num(hand)
            self.rcHand[1-i].SetWidth(pokerW + (num - 1) * self.pokerOffsetW)
            self.rcHand[1-i].SetHeight(pokerH)
            y = y - pokerH - self.blankH

    # reponse window resize
    def OnSize(self, e):
        width, height = self.GetClientSize()
        self._Buffer = wx.EmptyBitmap(width, height)
        
        self.btn_start.MoveXY(width - 110, height - 50)
        self.btn_estimate.MoveXY(width - 110, height - 90)
        self.cb_rule.MoveXY(width - 100, height - 120)
        self.CalcRect()        
        self.Refresh()
        
app = wx.App(False)
frame = GameFrame(None, 'libqp test app - gp')
frame.Show()
app.MainLoop()
