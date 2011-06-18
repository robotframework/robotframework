public class  JavaLibUsingTimestamps {

    public void javaTimestamp() throws InterruptedException {
        System.out.println("*INFO:1308419034931* Known timestamp");
        System.out.println("*HTML:" +
                           System.currentTimeMillis() +
                           "*<b>Current</b>");
        Thread.sleep(100);
    }
}
