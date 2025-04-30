# utilities

## AI-assisted coding

From [Karpathy](https://x.com/karpathy/status/1915581920022585597):

Noticing myself adopting a certain rhythm in AI-assisted coding (i.e. code I actually and professionally care about, contrast to vibe code).

1. Stuff everything relevant into context (this can take a while in big projects. If the project is small enough just stuff everything e.g. `files-to-prompt . -e ts -e tsx -e css -e md --cxml --ignore node_modules -o prompt.xml`)
2. Describe the next single, concrete incremental change we're trying to implement. Don't ask for code, ask for a few high-level approaches, pros/cons. There's almost always a few ways to do thing and the LLM's judgement is not always great. Optionally make concrete.
3. Pick one approach, ask for first draft code.
4. Review / learning phase: (Manually...) pull up all the API docs in a side browser of functions I haven't called before or I am less familiar with, ask for explanations, clarifications, changes, wind back and try a different approach.
6. Test.
7. Git commit.
Ask for suggestions on what we could implement next. Repeat.

Something like this feels more along the lines of the inner loop of AI-assisted development. The emphasis is on keeping a very tight leash on this new over-eager junior intern savant with encyclopedic knowledge of software, but who also bullshits you all the time, has an over-abundance of courage and shows little to no taste for good code. And emphasis on being slow, defensive, careful, paranoid, and on always taking the inline learning opportunity, not delegating. Many of these stages are clunky and manual and aren't made explicit or super well supported yet in existing tools. We're still very early and so much can still be done on the UI/UX of AI assisted coding.
