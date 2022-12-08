# import only needed modules
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
import sys


class ColorMenu(DropDown):
    # defined style in kivy doc
    def __init__(self, attached_widget, **kwargs):
        """
        ColorMenu widget to show color options as well as an option to delete the current attached widget
        :param attached_widget: widget to attach this dropdown to
        """
        super(ColorMenu, self).__init__(**kwargs)
        # open the dropdown list
        self.open(attached_widget)
        # save the widget that the dropdown list is attached to
        # in order to be used to get the parent layout
        self.attached_widget = attached_widget

    def change_color(self, data) -> None:
        """
        Change color of the attached widget
        :param data: rgba list (r, g, b, a)
        """
        # if the attached widget is of DragRect type, does not need to travel up to its container
        if self.attached_widget.__class__.__name__ == "DragRect":
            self.attached_widget.change_rect_color(data)
            return
        # else the attached widget is a button in LegendItem class, so travel up to the LegendItem instance's container
        self.attached_widget.parent.parent.parent.change_legend_color(data)

    def remove_widget(self) -> None:
        """
        Remove the attached widget from screen
        """
        # if the attached widget is of DragRect type, does not need to travel up to its container
        if self.attached_widget.__class__.__name__ == "DragRect":
            self.attached_widget.remove_rect()
            return
        # else the attached widget is a button in LegendItem class, so travel up to the LegendItem instance's container
        self.attached_widget.parent.parent.parent.remove_legend()


class LegendItemWidget(Widget):
    # defined style in kivy doc

    # color rgba property for the legend item's color (r, g, b, a)
    legend_color = ListProperty((0, 0, 0.8, 1))

    def __init__(self):
        super(LegendItemWidget, self).__init__()

    def remove_legend(self) -> None:
        """
        Function to bind to save schedule btn. Take an image of the schedule screen and save it
        """
        # clear all widgets in the layout
        self.clear_widgets()

        # reduce the layout's rows
        # delete the widget from the parent layout
        self.parent.rows -= 1
        self.parent.remove_widget(self)

    def change_legend_color(self, data) -> None:
        """
        Change the color of the legend item based on the given color
        :param data: rgba list (r, g, b, a)
        """
        self.legend_color = data


class LegendWidget(RelativeLayout):
    # defined style in kivy doc
    def __init__(self, **kwargs):
        super(LegendWidget, self).__init__(**kwargs)

    def add_legend(self):
        """
        Function to bind to add_legend btn. Add another legend item to the legend section.
        """
        legend_item_layout = self.ids.legend_item_layout

        # only allow up to 10 legend items
        if legend_item_layout.rows < 10:
            legend_item_layout.rows += 1
            legend_item_layout.add_widget(LegendItemWidget())

    def save_schedule(self):
        """
        Function to bind to save schedule btn. Take an image of the schedule screen and save it
        """
        # hide the save and add legend buttons before taking image
        self.ids.save.opacity = 0
        self.ids.add_legend.opacity = 0

        # take a pic of the app screen
        self.parent.export_to_png("schedule.png")

        # show the buttons again
        self.ids.add_legend.opacity = 1
        self.ids.save.opacity = 1


class CalendarWidget(BoxLayout):
    # defined style of widget in kivy doc
    def __init__(self, **kwargs):
        super(CalendarWidget, self).__init__(**kwargs)


class DragRect(Button):
    # defined style in kivy doc

    # color rgba property for the rectangle's color
    rect_color = ListProperty((0, 0, 0.8, 1))
    
    def __init__(self, **kwargs):
        super(DragRect, self).__init__(**kwargs)

    def change_rect_color(self, data) -> None:
        """
        Change color of the rectangle
        :param data: rgba list (r, g, b, a)
        """
        self.rect_color = data

    def remove_rect(self) -> None:
        """
        Remove this rect from its parent container and thus the screen
        """
        self.parent.remove_rect_from_list(self)
        self.parent.remove_widget(self)

    def collide_point(self, x, y) -> bool:
        """
        Check if there is a collision of this rectangle with the given point (x,y)
        :param x: x-coordinate of the point
        :param y: y-coordinate of the point
        :return: True if there is a collision; False otherwise.
        """
        # left x coord of rect
        left = self.x
        # right x coord of rect
        right = self.right
        # bottom y coord of rect
        bottom = self.top
        # top y coord of rect
        top = self.y

        # return True if the given point is within the rect's boundaries
        if top > y > bottom and right > x > left:
            return True
        return False

    def collide_widget(self, widget) -> bool:
        """
        Check if there is a collision of this rectangle with another widget
        :param widget: the widget instance to check for collision with
        :return: True if there is a collision; False otherwise.
        """
        # bottom y coord of rect
        bottom = self.top
        # top y coord of rect
        top = self.y

        # bottom y coord of given rect
        widget_bottom = widget.top
        # top y coord of given rect
        widget_top = widget.y

        # check if any one the given rect's boundaries are within the rect's boundaries
        # or if the rect is within the given rect's boundaries
        if top >= widget_bottom >= bottom or top >= widget_top >= bottom or (widget_top > top and widget_bottom < bottom):
            return True
        return False


class HourLines(RelativeLayout):
    # defined style in kivy doc
    pass


class TimeLines(FloatLayout):
    # defined style in kivy doc

    # property to specify the name of the day when creating this widget
    day_text = StringProperty()

    def __init__(self, **kwargs):
        super(TimeLines, self).__init__(**kwargs)

        # rectangle to be drawn whenever the user drags their mouse on this layout
        self.rect = None

        # rect_list to keep track of what rects are in the day
        # in order to prevent any newly created rect from having collision with any of these rects
        self.rect_list = []

    def remove_rect_from_list(self, rect) -> None:
        """
        Remove the given rectangle instance from the list of existing rectangle instances in this layout
        :param rect: rectangle instance to be removed
        """
        self.rect_list.remove(rect)

    def on_touch_down(self, touch) -> bool:
        """
        Override parent's mouse touch down event.
        Start a new rectangle instance when the user clicks on the grid layout.
        :param touch: the position of the user's mouse-down event
        :return: True if the event was handled properly; False otherwise.
        """
        # detect whether there is already a rect at touch down event
        # if Yes, show a color menu
        for rect in self.rect_list:
            if rect.collide_point(touch.pos[0], touch.pos[1]):
                rect.dispatch('on_release')
                return True
        # if No, start a new rect object
        if self.collide_point(touch.pos[0], touch.pos[1]):
            self.rect = DragRect()
            self.rect.width = self.width
            self.rect.pos[0] = self.pos[0]
            self.rect.pos[1] = self._closest_start_time_y_coord(touch.pos[1]+10)-15
            # make sure that the pos returned by helper method is valid
            if self._closest_start_time_y_coord(touch.pos[1]+10) == -1:
                self.rect = None

            return True

    def on_touch_up(self, touch) -> bool:
        """
        Override the parent's mouse touch up event.
        Finish drawing the rectangle that was started in touch down event. This is to simulate the mouse-drag event.
        :param touch: the position of the user's mouse-up event.
        :return: True if the event was handled properly. False otherwise.
        """
        if self.rect is not None:
            # only allow dragging downwards, not upwards
            if touch.y >= self.rect.pos[1]:
                self.rect = None
                return True

            # configure the height of the rect
            if self._closest_end_time_y_coord(touch.pos[1]-10) == -1:
                self.rect = None
                return True
            # it's a negative sized rect because kivy has the origin of coord system in the bottom-left corner
            # and the rect that we want to draw should start at the top and end at the bottom
            self.rect.height = -self.rect.pos[1] + self._closest_end_time_y_coord(touch.pos[1]-10) +15

            # if the configured rect collides with another existing rect, do not draw the rect
            for rect in self.rect_list:
                if rect.collide_widget(self.rect):
                    self.rect = None
                    return True
            # else finish drawing the rect, and add it to existing rect list
            self.add_widget(self.rect)
            self.rect_list.append(self.rect)

            # immediately show color menu option when the user finishes drawing the rect on the calendar
            self.rect.dispatch('on_release')

            # reset the var after adding the rect to the screen
            self.rect = None
            return True

    def _closest_start_time_y_coord(self, touch_pos) -> int:
        """
        Helper method: get the closest y-coord given the y position of the mouse touch event.
        Used to align the top of the rect to a line in the grid
        :param touch_pos: y-coordinate of the user's touch event
        :return: y-coordinate
        """
        # method is to get the y position of the row that has the minimum difference with the touch's y-pos
        y_coord = -1
        min_difference = sys.maxsize
        for idx in range(len(self.children[-1].children)):
            child = self.children[-1].children[idx]
            if abs(child.pos[1] - touch_pos) < min_difference:
                y_coord = child.pos[1]
                min_difference = abs(child.pos[1] - touch_pos)

        return y_coord

    def _closest_end_time_y_coord(self, touch_pos) -> int:
        """
        Helper method: get the closest y-coord given the y position of the mouse up event.
        Used to align the bottom of the rect to a line in the grid
        :param touch_pos: y-coordinate of the user's touch event
        :return: y-coordinate
        """
        # method is to get the y position of the row that has the minimum difference with the touch's y-pos
        row_idx = -1
        min_difference = sys.maxsize
        for idx in range(len(self.children[-1].children)):
            child = self.children[-1].children[idx]
            if abs(child.y - touch_pos) < min_difference:
                row_idx = idx
                min_difference = abs(child.y - touch_pos)

        # the use the row index to calculate the y pos because the grid is divided evenly into 25 rows
        return row_idx * self.height // 25