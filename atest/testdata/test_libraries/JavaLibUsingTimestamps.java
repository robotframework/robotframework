import java.util.GregorianCalendar;

public class  JavaLibUsingTimestamps {

    public void javaTimestamp() throws InterruptedException {
        long timestamp = 1308419034931L;
        GregorianCalendar calendar = new GregorianCalendar();
        calendar.setTimeInMillis(timestamp);
        timestamp += 10800000 - calendar.getTimeZone().getOffset(calendar.getTimeInMillis());
        System.out.println("*INFO:" + timestamp +"* Known timestamp");
        System.out.println("*HTML:" +
                           System.currentTimeMillis() +
                           "*<b>Current</b>");
        Thread.sleep(100);
    }
}
