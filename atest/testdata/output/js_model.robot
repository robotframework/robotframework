*** Settings ***
Documentation    </script>
Metadata    </script>    </script>
Force Tags    </script>
Resource    </script>

*** Test Cases ***
</script>
    [Documentation]    FAIL </script>
    [Timeout]    10s
    Log    </script>
    </script>

HTML </script>
    Log    <b>HTML</b></script>    HTML
    Fail    *HTML* <b>HTML</b></script>

Test With HTML Doc
    [Documentation]    *HTML* <b>Bold Documentation</b>
    Log    Test passed

*** Keywords ***
</script>
    [Documentation]    </script>
    [Timeout]    10s
    Fail    </script>
