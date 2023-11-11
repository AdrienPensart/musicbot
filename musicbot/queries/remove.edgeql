update Music
filter contains(.paths, <str>$path)
set {folders := (select .folders filter @path != <str>$path)};
