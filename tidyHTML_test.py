import unittest
from tidyHTML import *


class TidyHTML(unittest.TestCase):

    def test_process_start_tag(self):
        line = "Let's <abc> test <XYZ extra> this"

        self.assertEqual(process_start_tag(line, 6), "abc")
        self.assertEqual(process_start_tag(line, 17), "xyz")


    def test_process_end_tag(self):
        line = "Here </are> some </END> tags"

        self.assertEqual(process_end_tag(line, 5), "are")
        self.assertEqual(process_end_tag(line, 17), "end")


    def test_insert_end_tag(self):
        start_tag_list = ["abc", "def"]
        global_start_tag_list = ["xyz", "abc", "def"]
        
        line = 'Hark </abc> what light'
        position = 5

        self.assertEqual(insert_end_tag(line, position, start_tag_list),
                         ('Hark </def></abc> what light', 11, ["abc"]))


    def test_correct_capitalization(self):
        line = 'I <wiSh> you </HAD> more time'

        self.assertEqual(correct_capitalization(line, 2, "wiSh", True),
                         'I <wish> you </HAD> more time')
        self.assertEqual(correct_capitalization(line, 13, "HAD", False),
                         'I <wiSh> you </had> more time')


    def test_start_tag_function(self):
        start_tag_list = ["abc", "def"]
        global_start_tag_list = ["xyz", "abc", "def"]

        line = "Only <abc> fools <def> rush <in>"
        position = 28

        self.assertEqual(start_tag_function(line, position, start_tag_list),
                         ("Only <abc> fools <def> rush <in>", 31,
                          ["abc", "def", "in"]))


    def test_end_tag_function(self):
        global_start_tag_list = ["xyz", "abc", "def"]
        start_tag_list = ["def"]
        end_tag_list = []

        line = "I am <def>initely </def></not> going"
        position = 18

        self.assertEqual(end_tag_function(line, position, start_tag_list,
                                          end_tag_list),
                         ("I am <def>initely </def></not> going", 24, [], []))
        

    def test_correct_tag_nesting(self):
        line = 'I <did> not <see> that </did>'

        self.assertEqual(correct_tag_nesting(line),
                         ('I <did> not <see> that </see></did>', [], []))

        line = "<huh> that's weird"

        self.assertEqual(correct_tag_nesting(line),
                         ("<huh> that's weird", ["huh"], []))


    def test_dealing_with_special_tags(self):
        line = 'How to get a<head>'

        self.assertEqual(dealing_with_special_tags(line),
                         "How to get a\n<head>")

        line = "<h1> is a tag"

        self.assertEqual(dealing_with_special_tags(line),
                         "\n<h1> is a tag")


    def test_start_tag_correct_indentation(self):
        line = "  some text<a> some other text"
        indentation = 1
        start_tag_list = ['a']

        self.assertEqual(start_tag_correct_indentation(line,
                                                       indentation,
                                                       start_tag_list),
                         ("  some text\n  <a> some other text", 1, ['a']))


        line = "  some text<a> some<b>other text"
        indentation = 1
        start_tag_list = ['a', 'b']

        self.assertEqual(start_tag_correct_indentation(line,
                                                       indentation,
                                                       start_tag_list),
                         ("  some text\n  <a> some\n    <b>other text", 1,
                          ['a', 'b']))

    def test_end_tag_correct_indentation(self):
        global_start_tag_list = ["xyz", "abc", "def"]
        end_tag_list = ['def']
        line = '      Here is </def>the tag'
        indentation = 3

        self.assertEqual(end_tag_correct_indentation(line,
                                                     indentation,
                                                     end_tag_list),
                         ("      Here is \n    </def>\n    the tag", 3, ['def']))

    def test_correct_indentation(self):
        global_start_tag_list = ["xyz", "abc", "def"]
        end_tag_list = ['def']
        line = 'This should </def> work'
        indentation = 3

        self.assertEqual(correct_indentation(line, indentation, [], end_tag_list),
                         ("      This should \n    </def>\n     work"))

        global_start_tag_list = ["xyz", "abc", "def"]
        start_tag_list = ['a']
        line = 'Introducing <a> new start tag'
        indentation = 3

        self.assertEqual(correct_indentation(line, indentation,
                                             start_tag_list, []),
                         ("      Introducing \n      <a> new start tag"))

    def test_generate_line_list(self):
        line = "<a>\n new line\n"
        pos = 0
        break_pos = 3
        line_list = []

        self.assertEqual(generate_line_list(break_pos, line_list, pos, line),
                         (["<a>", "\n new line\n"]))

        line = "A <sen>tence\n about line breaks\n"
        pos = 0
        break_pos = 12
        line_list = []

        self.assertEqual(generate_line_list(break_pos, line_list, pos, line),
                         (["A <sen>tence", "\n about line breaks\n"]))


    def test_separate_line_into_segments(self):
        line_list = (["A looooong line A looooong line A looooong line A looooong line A looooong line A looooong line A looooong line A looooong line",
                      "\n a shorter line\n"])
        sub_line = "A looooong line A looooong line A looooong line A looooong line A looooong line A looooong line A looooong line A looooong line"
        i = 0

        self.assertEqual(separate_line_into_segments(sub_line, line_list, i),
                         ("A looooong line A looooong line A looooong line A looooong line A looooong line ",
                          ["A looooong line A looooong line A looooong line A looooong line A looooong line ",
                           "\nA looooong line A looooong line A looooong line",
                           "\n a shorter line\n"]))

    def test_line_length_correction(self):
        line = "  This is going to be a really long line, and I apologize that I cannot find a way to make it easier to read\n"

        self.assertEqual(line_length_correction(line),
                         "  This is going to be a really long line, and I apologize that I cannot find a \n  way to make it easier to read\n")

        line = "There is some whitespace here:     "

        self.assertEqual(line_length_correction(line),
                         "There is some whitespace here:\n")


    def test_remove_end_whitespace(self):
        line_list = ["Here's whitespace    \n", "And here, too   \n"]
        sub_line1 = "Here's whitespace    \n"
        i = 0

        self.assertEqual(remove_end_whitespace(sub_line1, line_list, i),
                         ("Here's whitespace\n",
                          ["Here's whitespace\n", "And here, too   \n"]))

unittest.main()
