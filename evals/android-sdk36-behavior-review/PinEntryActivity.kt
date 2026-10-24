class PinEntryActivity : Activity() {
    private lateinit var notice: TextView
    private lateinit var pin: EditText
    private lateinit var counter: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        counter = TextView(this)
        pin = EditText(this).apply {
            hint = "One-time code"
            inputType = InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_VARIATION_PASSWORD
            transformationMethod = null
            addTextChangedListener(object : TextWatcher {
                override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}

                override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                    counter.text = "${s?.length ?: 0} of 6"
                    counter.announceForAccessibility(counter.text)
                }

                override fun afterTextChanged(s: Editable?) {}
            })
        }
        notice = TextView(this).apply {
            text = "We sent a code to your phone"
            visibility = View.VISIBLE
        }
        setContentView(
            LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                addView(notice)
                addView(pin)
                addView(counter)
            },
        )
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (notice.visibility == View.VISIBLE) {
            notice.visibility = View.GONE
        } else {
            super.onBackPressed()
        }
    }
}
