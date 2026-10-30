from dataclasses import dataclass, field

# note- rules i'm considering for blocking inputs. Input sanitization is the first big roadblock. (pass-off to LLM judgement? their TOS pretty strict.)
BLOCKED_DOMAINS = frozenset([]) # note- link can be obfuscated
BLOCKED_WORDS = frozenset([]) # note- keywords can be obfuscated and i'm assuming english only. 


@dataclass
class Anchors:
    """
    A class representing user's seeded input to anchor a search. 
    This includes text-based fields including name, keywords, associations and links.
    Names and keywords are required fields, while associations, links, and notes are optional.
    """

    names: list[str] = field(default_factory=list, doc="Names or aliases of individual.")
    keywords: list[str] = field(default_factory=list, doc="Keywords related to the individual.")
    associations: list[str] = field(default_factory=list, doc="Organizations, groups, or other entities the individual is known to be affiliated with.")
    links: list[str] = field(default_factory=list, doc="Links related to the individual.")
    notes: str = field(default="", doc="Additional notes or context about the individual.")

    
    def __post_init__(self):
        """
        Cleans and validates the fields of user-input anchors.
        """
        # Clean and validate fields
        cleaned_fields = {}
        # Handle list fields for erroneous entries and strip whitespace
        for field_name in ['names', 'keywords', 'associations', 'links']:
            value = getattr(self, field_name)
            if isinstance(value, str):
                value = [value]
            if not isinstance(value, list):
                raise TypeError(f"{field_name} must be a list of strings.")
            if not all(isinstance(x, str) for x in value):
                raise TypeError(f"All elements in {field_name} must contain only strings.")
            cleaned_fields[field_name] = [x.strip() for x in value if x.strip()]
                
        # Cleans notes field and final pass validation
        for field_name, value in cleaned_fields.items():
            setattr(self, field_name, value)
        if not isinstance(self.notes, str):
            raise TypeError("Notes must be a string.")
        self.notes = self.notes.strip()
        if not self.names or not self.keywords:
            raise ValueError("Please provide information to anchor searching. Name and at least one keyword is required.")


# Test cases for Anchors class.
if __name__ == "__main__":
    cases = [
        ("valid input cleaned",
         lambda: Anchors(names=[" Lord Bogmire ", "  "], keywords="benevolent", notes="  ultimate slab  "),
         lambda a: a.names == ["Lord Bogmire"] and a.keywords == ["benevolent"] and a.notes == "ultimate slab"),
        ("empty",         lambda: Anchors(),                                              ValueError),
        ("blank name",    lambda: Anchors(names=["  "], keywords=["log"]),               ValueError),
        ("None keywords", lambda: Anchors(names=["Bog"], keywords=None),                  TypeError),
        ("bad notes",     lambda: Anchors(names=["Bog"], keywords=["log"], notes=42),    TypeError),
        ("non-str item",  lambda: Anchors(names=["Bog", 42], keywords=["log"]),          TypeError),
        ("only names+notes / no keywords",  lambda: Anchors(names=["Bog"], notes="ultimate slab"), ValueError),
        ("link spaces",  lambda: Anchors(names=["Bog"], keywords=["log"], links=["  https://mincemeatjenkins.com  "]), lambda a: a.links == ["https://mincemeatjenkins.com"]),
        ("blank keywords",  lambda: Anchors(names=["Bog"], keywords=["  ", "    ", "              "]), ValueError),
    ]

    passed = 0
    for label, make, expected in cases:
        expects_error = isinstance(expected, type) and issubclass(expected, Exception)
        try:
            result = make()
            ok = not expects_error and expected(result)
            detail = "" if ok else f"got {result!r}"
        except Exception as e:
            ok = expects_error and isinstance(e, expected)
            detail = "" if ok else f"raised {type(e).__name__}: {e}"
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f"  ({detail})" if detail else ""))

    print(f"\n{passed}/{len(cases)} passed")



