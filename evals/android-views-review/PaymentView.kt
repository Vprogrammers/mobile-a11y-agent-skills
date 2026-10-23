class PaymentView(context: Context) : View(context) {
    private var amount = 0

    init {
        setOnTouchListener { _, event ->
            if (event.action == MotionEvent.ACTION_UP) amount++
            true
        }
    }

    override fun onDraw(canvas: Canvas) {
        canvas.drawText("Amount: $amount", 20f, 40f, Paint())
        canvas.drawCircle(60f, 100f, 28f, Paint())
    }
}
