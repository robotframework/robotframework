Reproducible Builds
===================

Robot Framework honors the `SOURCE_DATE_EPOCH
<https://reproducible-builds.org/docs/source-date-epoch/>` environment
variable so that it can be built in a reproducible fashion.  When the
`SOURCE_DATE_EPOCH` environment variable is set, timestamps embedded
in generated documentation and log messages are set to its fixed
value.
